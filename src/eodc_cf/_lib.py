"""Pre-configured CFCoordinate subclasses."""

from typing import Any

from eodc_cf._core import CFCoordinate


class CFLonCoordinate(CFCoordinate):
    """Geographic longitude coordinate (degrees_east, axis X)."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            standard_name="longitude",
            long_name="longitude",
            units="degrees_east",
            axis="X",
            **kwargs,
        )


class CFLatCoordinate(CFCoordinate):
    """Geographic latitude coordinate (degrees_north, axis Y)."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            standard_name="latitude",
            long_name="latitude",
            units="degrees_north",
            axis="Y",
            **kwargs,
        )


class CFXCoordinate(CFCoordinate):
    """Projected x coordinate (meters, axis X)."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            standard_name="projection_x_coordinate",
            long_name="x coordinate of projection",
            units="meters",
            axis="X",
            **kwargs,
        )


class CFYCoordinate(CFCoordinate):
    """Projected y coordinate (meters, axis Y)."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            standard_name="projection_y_coordinate",
            long_name="y coordinate of projection",
            units="meters",
            axis="Y",
            **kwargs,
        )


class CFTimeCoordinate(CFCoordinate):
    """Temporal coordinate (axis T); units must be supplied by the caller."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(standard_name="time", axis="T", **kwargs)


if __name__ == "__main__":
    pass
