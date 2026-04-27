import copy
import re
from typing import Annotated, Union

from pydantic import AfterValidator, BaseModel, Field


def validate_variable_name(input: str) -> str:
    pattern = re.compile(r"^[a-z][a-z_0-9]*$")

    if not pattern.match(input):
        raise Exception(
            f"String '{input}' does not comply with the CF naming convention."
        )

    return input


def validate_long_name(input: str | None) -> str:
    pattern = re.compile(r"^[a-z_0-9][a-z_0-9\s(),]+$")

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


def validate_attributes(input: dict | None) -> dict:
    input = input or {}
    for k in input.keys():
        validate_variable_name(k)

    return input


class CFBase(BaseModel):
    name: Annotated[str, AfterValidator(validate_variable_name)]
    standard_name: Annotated[str, AfterValidator(validate_variable_name)] = Field(
        ..., min_length=2, max_length=50
    )
    long_name: Annotated[str, AfterValidator(validate_long_name)] | None = None


class CFCoordinate(CFBase):
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
    fill_value: int | float | None = 0
    valid_range: tuple[int | float, int | float] | None = None
    grid_mapping: Annotated[str, AfterValidator(validate_variable_name)] = None
    other_attrs: Annotated[dict, AfterValidator(validate_attributes)] | None = {}

    _coordinates = {}

    def __init__(self, cf_coords: list[CFCoordinate] | None = None, **kwargs):
        super().__init__(**kwargs)
        if cf_coords:
            for cf_coord in cf_coords:
                if isinstance(cf_coord, CFCoordinate):
                    self._coordinates[cf_coord.name] = cf_coord

    def __add__(self, other: CFCoordinate) -> "CFDataVariableBase":
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
    scale_factor: int | float | None = 1.0
    add_offset: int | float | None = 0
    units: str | None = None


class CFFlagVariable(CFDataVariableBase):
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
    title: str
    source: str
    institution: str | None = "EODC"
    history: str | None = None
    references: list[str] | None = None
    comment: str | None = None
    other_attrs: Annotated[dict, AfterValidator(validate_attributes)] | None = {}

    _variables = {}

    @property
    def variables(self) -> dict[str, CFDataVariable | CFFlagVariable]:
        return self._variables

    def __init__(
        self, cf_vars: list[CFDataVariable | CFFlagVariable] | None = None, **kwargs
    ):
        super().__init__(**kwargs)
        if cf_vars:
            for cf_var in cf_vars:
                if isinstance(cf_var, CFDataVariable | CFFlagVariable):
                    self._variables[cf_var.name] = cf_var

    def __add__(
        self, other: Union["CFDataset", CFDataVariable, CFFlagVariable]
    ) -> "CFDataset":
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


class CFMultiscaleLayout(BaseModel):
    id: str
    cell_size: tuple[float, float]
    path: str | None = None
    derived_from: str | None = None
    factors: tuple[float, float] | None = None
    resampling_method: Annotated[str, AfterValidator(validate_variable_name)] | None = (
        None
    )


def validate_ms_layouts(input: list[CFMultiscaleLayout]) -> list[CFMultiscaleLayout]:
    ids = []
    for layout in input:
        if layout.id in ids:
            raise KeyError(
                f"{layout.id} appears multiple times. Each layout element needs to have a unique ID."
            )
        ids.append(layout.id)

    return input


def validate_resampling_method(rm: str | None, grp_rm: str | None) -> bool:
    res_match = True
    if grp_rm is not None and rm is not None:
        res_match = grp_rm == rm

    return res_match


class CFMultiscaleAttributes(BaseModel):
    layout: Annotated[list[CFMultiscaleLayout], AfterValidator(validate_ms_layouts)]
    version: str = "1.0"
    tile_matrix_ref: str | None = None
    resampling_method: Annotated[str, AfterValidator(validate_variable_name)] | None = (
        None
    )
    overview_variables: (
        list[Annotated[str, AfterValidator(validate_variable_name)]] | None
    ) = None

    @property
    def ids(self) -> list[str]:
        return [layout.id for layout in self.layout]

    def __add__(self, other: CFMultiscaleLayout) -> "CFMultiscaleAttributes":
        new_id = other.id not in self.ids
        rm_match = validate_resampling_method(
            other.resampling_method, self.resampling_method
        )
        if new_id and rm_match:
            self.layout.append(other)

        return self

    def __len__(self) -> int:
        return len(self.layout)


class CFMultiscaleDataset(CFDataset):
    multiscales: CFMultiscaleAttributes


if __name__ == "__main__":
    pass
