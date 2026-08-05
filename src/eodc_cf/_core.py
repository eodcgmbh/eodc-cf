"""Core Pydantic models for CF convention variables and datasets."""

import copy
import re
from typing import Annotated, Any, Union

from pydantic import AfterValidator, BaseModel


def validate_variable_name(arg: str) -> str:
    """Validate a CF variable/standard name.

    Returns arg unchanged if it starts with a letter and holds only letters,
    digits, and underscores; raises ValueError otherwise.
    """
    pattern = re.compile(r"^[a-zA-Z][a-zA-Z_0-9]*$")

    if not pattern.match(arg):
        err_msg = f"String '{arg}' does not comply with the CF naming convention."
        raise ValueError(err_msg)

    return arg


def validate_attribute_name(arg: str) -> str:
    """Validate a CF attribute name.

    Returns arg unchanged if it starts with a letter and holds only letters,
    digits, underscores, and colons; raises ValueError otherwise.
    """
    pattern = re.compile(r"^[a-zA-Z][a-zA-Z_0-9:]*$")

    if not pattern.match(arg):
        err_msg = f"Attribute '{arg}' does not comply with the CF naming convention."
        raise ValueError(err_msg)

    return arg


def validate_long_name(arg: str | None) -> str:
    """Validate a CF long name.

    Returns arg unchanged if it is None or holds only letters, digits,
    whitespace, and `(),`; raises ValueError otherwise.
    """
    pattern = re.compile(r"^[a-zA-Z_0-9][a-zA-Z_0-9\s(),]+$")

    if arg and not pattern.match(arg):
        err_msg = f"Long name '{arg}' does not comply with the CF naming convention."
        raise ValueError(err_msg)

    return arg


def validate_axis_name(arg: str | None) -> str:
    """Validate a CF axis name.

    Returns arg unchanged if it is None or a single uppercase letter;
    raises ValueError otherwise.
    """
    pattern = re.compile(r"^[A-Z]$")

    if arg and not pattern.match(arg):
        err_msg = f"Axis name '{arg}' does not comply with the CF naming convention."
        raise ValueError(err_msg)

    return arg


def validate_attributes(arg: dict | None) -> dict:
    """Validate a dict of CF attributes.

    Returns arg (or an empty dict if None) after validating every key as a
    CF attribute name.
    """
    arg = arg or {}
    for k in arg:
        validate_attribute_name(k)

    return arg


class CFBase(BaseModel):
    """Shared base model providing name, standard_name, and optional long_name."""

    name: Annotated[str, AfterValidator(validate_variable_name)]
    standard_name: Annotated[str, AfterValidator(validate_variable_name)]
    long_name: Annotated[str, AfterValidator(validate_long_name)] | None = None


class CFCoordinate(CFBase):
    """CF coordinate variable."""

    axis: Annotated[str, AfterValidator(validate_axis_name)] | None = None
    units: str | None = None
    other_attrs: Annotated[dict, AfterValidator(validate_attributes)] | None = {}

    @property
    def attrs(self) -> dict:
        """Return CF-compliant metadata as a dict.

        Merges other_attrs with the model fields (name excluded).
        """
        attrs = super().model_dump(exclude=["name", "other_attrs"], exclude_none=True)
        metadata = copy.deepcopy(self.other_attrs)
        metadata.update(attrs)

        return metadata


class CFDataVariableBase(CFBase):
    """CF data variables model; supports attaching coordinates via + operator."""

    fill_value: int | float | None = 0
    valid_range: tuple[int | float, int | float] | None = None
    grid_mapping: Annotated[str, AfterValidator(validate_variable_name)] = None
    other_attrs: Annotated[dict, AfterValidator(validate_attributes)] | None = {}

    _coordinates = {}

    def __init__(
        self, cf_coords: list[CFCoordinate] | None = None, **kwargs: Any
    ) -> None:
        """Initialize the variable and optionally register a list of CF coordinates."""
        super().__init__(**kwargs)
        if cf_coords:
            for cf_coord in cf_coords:
                if isinstance(cf_coord, CFCoordinate):
                    self._coordinates[cf_coord.name] = cf_coord

    def __add__(self, other: CFCoordinate) -> "CFDataVariableBase":
        """Attach a CFCoordinate to this variable and return self.

        Non-CFCoordinate values are ignored, which allows chaining `+`.
        """
        if isinstance(other, CFCoordinate):
            self._coordinates.update({other.name: other})

        return self

    def __len__(self) -> int:
        """Return the number of attached coordinates."""
        return len(self._coordinates)

    @property
    def attrs(self) -> dict:
        """Return CF-compliant metadata as a dict.

        Renames fill_value to _FillValue and merges with other_attrs.
        """
        attrs = super().model_dump(
            exclude=["name", "fill_value", "other_attrs"], exclude_none=True
        )
        if self.fill_value is not None:
            attrs["_FillValue"] = self.fill_value
        metadata = copy.deepcopy(self.other_attrs)
        metadata.update(attrs)

        return metadata

    @property
    def coordinates(self) -> dict[str, CFCoordinate]:
        """Return the attached CFCoordinate instances, keyed by their name."""
        return self._coordinates


class CFDataVariable(CFDataVariableBase):
    """CF data variable with scale_factor, add_offset, and units."""

    scale_factor: int | float | None = 1.0
    add_offset: int | float | None = 0
    units: str | None = None


class CFFlagVariable(CFDataVariableBase):
    """CF flag variable encoding discrete boolean or bitwise states."""

    fill_value: int | None = 255
    flag_values: list
    flag_masks: list | None = None
    flag_meanings: list[Annotated[str, AfterValidator(validate_long_name)]]

    @property
    def attrs(self) -> dict:
        """Return CF-compliant metadata as a dict.

        Joins flag_meanings into a single space-separated string.
        """
        metadata = super().attrs
        metadata["flag_meanings"] = " ".join(metadata["flag_meanings"])
        return metadata


class CFDataset(BaseModel):
    """CF dataset holding global attributes and data variables."""

    title: str
    source: str
    institution: str | None = "eodc"
    history: str | None = None
    references: list[str] | None = None
    Conventions: str = "CF-1.11"
    comment: str | None = None
    other_attrs: Annotated[dict, AfterValidator(validate_attributes)] | None = {}

    _variables = {}

    @property
    def variables(self) -> dict[str, CFDataVariable | CFFlagVariable]:
        """Return the attached CF data/flag variables, keyed by their name."""
        return self._variables

    def __init__(
        self,
        cf_vars: list[CFDataVariable | CFFlagVariable] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the dataset and register a list of CF data variables."""
        super().__init__(**kwargs)
        if cf_vars:
            for cf_var in cf_vars:
                if isinstance(cf_var, CFDataVariable | CFFlagVariable):
                    self._variables[cf_var.name] = cf_var

    def __add__(
        self, other: Union["CFDataset", CFDataVariable, CFFlagVariable]
    ) -> "CFDataset":
        """Merge another CFDataset, or attach a single data/flag variable.

        Returns self; other types are ignored.
        """
        if isinstance(other, CFDataset):
            self._variables.update(other.variables)
        elif isinstance(other, CFDataVariable | CFFlagVariable):
            self._variables.update({other.name: other})

        return self

    def __len__(self) -> int:
        """Return the number of attached variables."""
        return len(self._variables)

    @property
    def attrs(self) -> dict:
        """Return CF-compliant global attributes as a dict.

        Joins a references list into a single semicolon-separated string.
        """
        attrs = super().model_dump(exclude=["other_attrs"], exclude_none=True)
        metadata = copy.deepcopy(self.other_attrs)
        metadata.update(attrs)
        if ("references" in metadata) and isinstance(metadata["references"], list):
            metadata["references"] = ";".join(metadata["references"])

        return metadata


if __name__ == "__main__":
    pass
