from eodc_cf._core import CFCoordinate


class CFLonCoordinate(CFCoordinate):
    def __init__(self, **kwargs):
        super().__init__(
            standard_name="longitude",
            long_name="longitude",
            units="degrees_east",
            axis="X",
            **kwargs,
        )


class CFLatCoordinate(CFCoordinate):
    def __init__(self, **kwargs):
        super().__init__(
            standard_name="latitude",
            long_name="latitude",
            units="degrees_north",
            axis="Y",
            **kwargs,
        )


class CFXCoordinate(CFCoordinate):
    def __init__(self, **kwargs):
        super().__init__(
            standard_name="projection_x_coordinate",
            long_name="x coordinate of projection",
            units="meters",
            axis="X",
            **kwargs,
        )


class CFYCoordinate(CFCoordinate):
    def __init__(self, **kwargs):
        super().__init__(
            standard_name="projection_y_coordinate",
            long_name="y coordinate of projection",
            units="meters",
            axis="Y",
            **kwargs,
        )


class CFTimeCoordinate(CFCoordinate):
    def __init__(self, **kwargs):
        super().__init__(standard_name="time", axis="T", **kwargs)


if __name__ == "__main__":
    pass
