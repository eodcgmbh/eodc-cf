"""Core Pydantic models for CF convention variables and datasets."""

import copy
import re
from typing import Annotated, Any, Union

from pydantic import AfterValidator, BaseModel, Field


def validate_variable_name(arg: str) -> str:
    """Check if input does not start with a letter or contains invalid characters."""
    pattern = re.compile(r"^[a-zA-Z][a-zA-Z_0-9]*$")

    if not pattern.match(arg):
        err_msg = f"String '{arg}' does not comply with the CF naming convention."
        raise ValueError(err_msg)

    return arg


def validate_attribute_name(arg: str) -> str:
    """Check if attribute does not contain invalid characters."""
    pattern = re.compile(r"^[a-zA-Z][a-zA-Z_0-9:]*$")

    if not pattern.match(arg):
        err_msg = f"Attribute '{arg}' does not comply with the CF naming convention."
        raise ValueError(err_msg)

    return arg


def validate_long_name(arg: str | None) -> str:
    """Check if input contains characters not permitted in a CF long name."""
    pattern = re.compile(r"^[a-zA-Z_0-9][a-zA-Z_0-9\s(),]+$")

    if arg and not pattern.match(arg):
        err_msg = f"Long name '{arg}' does not comply with the CF naming convention."
        raise ValueError(err_msg)

    return arg


def validate_axis_name(arg: str | None) -> str:
    """Check if input is not a single uppercase letter as required by CF conventions."""
    pattern = re.compile(r"^[A-Z]$")

    if arg and not pattern.match(arg):
        err_msg = f"Axis name '{arg}' does not comply with the CF naming convention."
        raise ValueError(err_msg)

    return arg


def validate_attributes(arg: dict | None) -> dict:
    """Check if any key in the dict is not a valid CF attribute name."""
    arg = arg or {}
    for k in arg:
        validate_attribute_name(k)

    return arg


class CFBase(BaseModel):
    """Shared base model providing name, standard_name, and optional long_name."""

    name: Annotated[str, AfterValidator(validate_variable_name)]
    standard_name: Annotated[str, AfterValidator(validate_variable_name)] = Field(
        ..., min_length=2, max_length=50
    )
    long_name: Annotated[str, AfterValidator(validate_long_name)] | None = None


class CFCoordinate(CFBase):
    """CF coordinate variable."""

    axis: Annotated[str, AfterValidator(validate_axis_name)] | None = None
    units: str | None = None
    other_attrs: Annotated[dict, AfterValidator(validate_attributes)] | None = {}

    @property
    def attrs(self) -> dict:
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
        """Attach a CFCoordinate to this variable and return self."""
        if isinstance(other, CFCoordinate):
            self._coordinates.update({other.name: other})

        return self

    def __len__(self) -> int:
        return len(self._coordinates)

    @property
    def attrs(self) -> dict:
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
        return self._coordinates


class CFDataVariable(CFDataVariableBase):
    """CF data variable with scale_factor, add_offset, and units."""

    scale_factor: int | float | None = 1.0
    add_offset: int | float | None = 0
    units: str | None = None


class CFFlagVariable(CFDataVariableBase):
    """CF flag variable encoding discrete states."""

    fill_value: int | None = 255
    flag_values: list
    flag_masks: list | None = None
    flag_meanings: list[Annotated[str, AfterValidator(validate_long_name)]]

    @property
    def attrs(self) -> dict:
        metadata = super().attrs
        metadata["flag_meanings"] = " ".join(metadata["flag_meanings"])
        return metadata


class CFDataset(BaseModel):
    """CF dataset holding global attributes and data variables."""

    title: str
    source: str
    institution: str | None = "EODC"
    history: str | None = None
    references: list[str] | None = None
    conventions: str = "CF-1.11"
    comment: str | None = None
    other_attrs: Annotated[dict, AfterValidator(validate_attributes)] | None = {}

    _variables = {}

    @property
    def variables(self) -> dict[str, CFDataVariable | CFFlagVariable]:
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
        """Merge another CFDataset or attach a single data variable."""
        if isinstance(other, CFDataset):
            self._variables.update(other.variables)
        elif isinstance(other, CFDataVariable | CFFlagVariable):
            self._variables.update({other.name: other})

        return self

    def __len__(self) -> int:
        return len(self._variables)

    @property
    def attrs(self) -> dict:
        attrs = super().model_dump(exclude=["other_attrs"], exclude_none=True)
        metadata = copy.deepcopy(self.other_attrs)
        metadata.update(attrs)

        return metadata


if __name__ == "__main__":
    pass
