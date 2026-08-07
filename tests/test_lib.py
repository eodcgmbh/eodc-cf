import pytest

from cf_cm_tree._lib import (
    CFLatCoordinate,
    CFLonCoordinate,
    CFTimeCoordinate,
    CFXCoordinate,
    CFYCoordinate,
)


def test_cf_lon_coordinate():
    cf_coord = CFLonCoordinate(name="lon")
    assert cf_coord.attrs == {
        "standard_name": "longitude",
        "long_name": "longitude",
        "units": "degrees_east",
        "axis": "X",
    }


def test_cf_lat_coordinate():
    cf_coord = CFLatCoordinate(name="lat")
    assert cf_coord.attrs == {
        "standard_name": "latitude",
        "long_name": "latitude",
        "units": "degrees_north",
        "axis": "Y",
    }


def test_cf_x_coordinate():
    cf_coord = CFXCoordinate(name="x")
    assert cf_coord.attrs == {
        "standard_name": "projection_x_coordinate",
        "long_name": "x coordinate of projection",
        "units": "meters",
        "axis": "X",
    }


def test_cf_y_coordinate():
    cf_coord = CFYCoordinate(name="y")
    assert cf_coord.attrs == {
        "standard_name": "projection_y_coordinate",
        "long_name": "y coordinate of projection",
        "units": "meters",
        "axis": "Y",
    }


def test_cf_time_coordinate():
    cf_coord = CFTimeCoordinate(name="t", units="days since 1990-1-1 0:0:0")
    assert cf_coord.attrs == {
        "standard_name": "time",
        "axis": "T",
        "units": "days since 1990-1-1 0:0:0",
    }


def test_cf_coordinate_kwargs_extend():
    cf_coord = CFXCoordinate(name="x", other_attrs={"grid": "epsg:4326"})
    assert cf_coord.standard_name == "projection_x_coordinate"
    assert cf_coord.attrs == {
        "standard_name": "projection_x_coordinate",
        "long_name": "x coordinate of projection",
        "units": "meters",
        "axis": "X",
        "grid": "epsg:4326",
    }


def test_cf_coordinate_kwargs_conflict():
    with pytest.raises(TypeError):
        CFXCoordinate(name="x", units="km")


if __name__ == "__main__":
    pass
