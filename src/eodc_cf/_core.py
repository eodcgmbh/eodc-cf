import copy
import re
from typing import Annotated, Union

from pydantic import AfterValidator, BaseModel, Field
from typing_extensions import TypedDict


def validate_variable_name(input: str) -> str:
    pattern = re.compile(r"^[a-z][a-z_0-9]*$")

    if not pattern.match(input):
        raise Exception(
            f"String '{input}' does not comply with the CF naming convention."
        )

    return input


def validate_long_name(input: str | None) -> str:
    pattern = re.compile(r"^[a-z_0-9][a-z_0-9\s]+$")

    if input and not pattern.match(input):
        raise Exception(
            f"Long name '{input}' does not comply with the CF naming convention."
        )

    return input


def validate_axis_name(input: str | None) -> str:
    pattern = re.compile(r"^[A-Z]$")

    if input and not pattern.match(input):
        raise Exception(
            f"Axis name '{input}' does not comply with the CF naming convention."
        )

    return input


class CFAttributes(TypedDict, total=False):
    name: Annotated[str, AfterValidator(validate_variable_name)] | None
    value: str


class CFBase(BaseModel):
    name: Annotated[str, AfterValidator(validate_variable_name)]
    standard_name: Annotated[str, AfterValidator(validate_variable_name)] = Field(
        ..., min_length=2, max_length=50
    )
    long_name: Annotated[str, AfterValidator(validate_long_name)] | None = None


class CFCoordinate(CFBase):
    axis: Annotated[str, validate_axis_name] | None = None
    units: str | None = None

    @property
    def attrs(self) -> dict:
        metadata = super().model_dump(exclude=["name"], exclude_none=True)
        return metadata


class CFDataVariableBase(CFBase):
    fill_value: float | None = 0
    valid_range: tuple | None = None
    grid_mapping: Annotated[str, AfterValidator(validate_variable_name)] = None
    other_attrs: CFAttributes | None = {}

    _coordinates = {}

    def __init__(self, cf_coords: list[CFCoordinate] | None = None, **kwargs):
        super().__init__(**kwargs)
        if cf_coords:
            for cf_coord in cf_coords:
                self._coordinates[cf_coord.name] = cf_coord

    def __add__(self, other: CFCoordinate) -> "CFDataVariableBase":
        if isinstance(other, CFCoordinate):
            self._coordinates.update({other.name: other})

        return self

    @property
    def attrs(self) -> dict:
        attrs = super().model_dump(
            exclude=["name", "fill_value", "other_attrs"], exclude_none=True
        )
        attrs["_FillValue"] = self.fill_value
        metadata = copy.deepcopy(self.other_attrs)
        metadata.update(attrs)

        return metadata

    @property
    def coordinates(self) -> dict[str, CFCoordinate]:
        return self._coordinates


class CFDataVariable(CFDataVariableBase):
    scale_factor: float | None = 1.0
    add_offset: float | None = 0
    units: str | None = None


class CFFlagVariable(CFDataVariableBase):
    flag_values: list
    flag_masks: list
    flag_meanings: list[Annotated[str, validate_long_name]]

    @property
    def attrs(self) -> dict:
        metadata = super().attrs
        metadata["flag_meanings"] = " ".join(metadata["flag_meanings"])
        return metadata


class CFDataset(BaseModel):
    title: str
    source: str
    institution: str | None = "EODC"
    history: str | None = None
    references: list[str] | None = None
    comment: str | None = None
    other_attrs: CFAttributes | None = {}

    _variables = {}

    @property
    def variables(self) -> dict[str, CFDataVariable | CFFlagVariable]:
        return self._variables

    def __init__(self, cf_vars: list[CFDataVariable] | None = None, **kwargs):
        super().__init__(**kwargs)
        if cf_vars:
            for cf_var in cf_vars:
                self._variables[cf_var.name] = cf_var

    def __add__(self, other: Union["CFDataset", CFDataVariable]) -> "CFDataset":
        if isinstance(other, CFDataset):
            self._variables.update(other.variables)
        elif isinstance(other, CFDataVariable):
            self._variables.update({other.name: other})

        return self

    @property
    def attrs(self) -> dict:
        attrs = super().model_dump(exclude=["other_attrs"], exclude_none=True)
        metadata = copy.deepcopy(self.other_attrs)
        metadata.update(attrs)

        return metadata


class CFMultiscaleLayout(BaseModel):
    id: str
    cell_size: tuple[float, float]
    path: str | None | None = None
    derived_from: str | None | None = None
    factors: tuple[float, float] | None | None = None
    resampling_method: (
        Annotated[str, AfterValidator(validate_variable_name)] | None | None
    ) = None


class CFMultiscaleAttributes(BaseModel):
    layout: list[CFMultiscaleLayout]
    version: str = "1.0"
    tile_matrix_ref: str | None | None = None
    resampling_method: (
        Annotated[str, AfterValidator(validate_variable_name)] | None | None
    ) = None
    overview_variables: (
        list[Annotated[str, AfterValidator(validate_variable_name)]] | None
    ) = None

    def __add__(self, other: CFMultiscaleLayout) -> "CFMultiscaleAttributes":
        self.layout.append(other)
        return self


class CFMultiscaleDataset(CFDataset):
    multiscales: CFMultiscaleAttributes


if __name__ == "__main__":
    pass
