from pydantic import BaseModel, Field, AfterValidator
from typing import Optional, Annotated, Union, List, Dict
from typing_extensions import TypedDict
import re
import copy


def validate_variable_name(input: str) -> str:
    pattern = re.compile(r'^[a-z][a-z_0-9]*$')

    if not pattern.match(input):
        raise Exception(f"String '{input}' does not comply with the CF naming convention.")
    
    return input


def validate_long_name(input: str | None) -> str:
    pattern = re.compile(r'^[a-z_0-9][a-z_0-9\s]+$')

    if input and not pattern.match(input):
        raise Exception(f"Long name '{input}' does not comply with the CF naming convention.")
    
    return input


def validate_axis_name(input: str | None) -> str:
    pattern = re.compile(r'^[A-Z]$')

    if input and not pattern.match(input):
        raise Exception(f"Axis name '{input}' does not comply with the CF naming convention.")
    
    return input


class CFAttributes(TypedDict, total=False):
    name: Optional[Annotated[str, AfterValidator(validate_variable_name)]]
    value: str


class CFBase(BaseModel):
    name: Annotated[str, AfterValidator(validate_variable_name)]
    standard_name: Annotated[str, AfterValidator(validate_variable_name)] = Field(..., min_length=2, max_length=50)
    long_name: Optional[Annotated[str, AfterValidator(validate_long_name)]] = None


class CFCoordinate(CFBase):
    axis: Optional[Annotated[str, validate_axis_name]] = None
    units: Optional[str] = None

    def to_dict(self) -> dict:
        metadata = super().model_dump(exclude=["name"], exclude_none=True)
        return metadata


class CFDataVariableBase(CFBase):
    fill_value: Optional[float] = 0
    valid_range: Optional[tuple] = None
    grid_mapping: Annotated[str, AfterValidator(validate_variable_name)] = None
    attrs: Optional[CFAttributes] = {}

    _coordinates = {}

    def __init__(self, cf_coords: list[CFCoordinate] | None = None, **kwargs):
        super().__init__(**kwargs)
        if cf_coords:
            for cf_coord in cf_coords:
                self._coordinates[cf_coord.name] = cf_coord

    def __add__(self, other: CFCoordinate) -> 'CFDataVariableBase':
        if isinstance(other, CFCoordinate):
            self._coordinates.update({other.name: other})

        return self
    
    def to_dict(self) -> dict:
        attrs = super().model_dump(exclude=["name", "fill_value", "attrs"], exclude_none=True)
        attrs["_FillValue"] = self.fill_value
        metadata = copy.deepcopy(self.attrs)
        metadata.update(attrs)

        return metadata
    

    @property
    def coordinates(self) -> Dict[str, CFCoordinate]:
        return self._coordinates


class CFDataVariable(CFDataVariableBase):
    scale_factor: Optional[float] = 1.
    add_offset: Optional[float] = 0
    units: Optional[str] = None


class CFFlagVariable(CFDataVariableBase):
    flag_values: list
    flag_masks: list
    flag_meanings: list[Annotated[str, validate_long_name]]

    def to_dict(self) -> dict:
        metadata = super().to_dict()
        metadata["flag_meanings"] = " ".join(metadata["flag_meanings"])
        return metadata


class CFDataset(BaseModel):
    title: str
    source: str
    institution: Optional[str] = "EODC"
    history: Optional[str] = None
    references: Optional[List[str]] = None
    comment: Optional[str] = None
    attrs: Optional[CFAttributes] = {}

    _variables = {}

    @property
    def variables(self) -> Dict[str, CFDataVariable | CFFlagVariable]:
        return self._variables
    
    def __init__(self, cf_vars: list[CFDataVariable] | None = None, **kwargs):
        super().__init__(**kwargs)
        if cf_vars:
            for cf_var in cf_vars:
                self._variables[cf_var.name] = cf_var

    def __add__(self, other: Union['CFDataset', CFDataVariable]) -> 'CFDataset':
        if isinstance(other, CFDataset):
            self._variables.update(other.variables)
        elif isinstance(other, CFDataVariable):
            self._variables.update({other.name: other})

        return self
    
    def to_dict(self) -> dict:
        attrs = super().model_dump(exclude=["attrs"], exclude_none=True)
        metadata = copy.deepcopy(self.attrs)
        metadata.update(attrs)

        return metadata
    

#__all__ = CFDataset

if __name__ == "__main__":
    pass
