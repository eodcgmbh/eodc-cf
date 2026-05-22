"""Entry point for eodc-cf."""

from eodc_cf._core import (
    CFCoordinate,
    CFDataset,
    CFDataVariable,
    CFFlagVariable,
)
from eodc_cf._lib import (
    CFLatCoordinate,
    CFLonCoordinate,
    CFTimeCoordinate,
    CFXCoordinate,
    CFYCoordinate,
)

__all__ = [
    "CFCoordinate",
    "CFDataVariable",
    "CFDataset",
    "CFFlagVariable",
    "CFLatCoordinate",
    "CFLonCoordinate",
    "CFTimeCoordinate",
    "CFXCoordinate",
    "CFYCoordinate",
]

name = "eodc_cf"
