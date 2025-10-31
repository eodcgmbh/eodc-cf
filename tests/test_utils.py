import numpy as np
import xarray as xr

from eodc_cf._core import CFDataset, CFDataVariable
from eodc_cf._lib import CFTimeCoordinate, CFXCoordinate, CFYCoordinate
from eodc_cf.utils import assign_cf_metadata


def test_assign_cf_md():
    da = xr.DataArray(
        np.zeros((2, 2, 2)),
        coords={"t": range(2), "y": range(2), "x": range(2)},
        dims=["t", "y", "x"],
    )
    ds = xr.Dataset({"var": da})

    cf_var = CFDataVariable(name="var", standard_name="var_name")
    cf_var = (
        cf_var
        + CFXCoordinate(name="x")
        + CFYCoordinate(name="y")
        + CFTimeCoordinate(name="t")
    )
    cf_ds = CFDataset(title="test_ds", source="tests")
    cf_ds = cf_ds + cf_var

    ds = assign_cf_metadata(ds, cf_ds)

    assert ds.attrs == {"title": "test_ds", "source": "tests", "institution": "EODC"}
    assert ds["var"].attrs == {
        "standard_name": "var_name",
        "_FillValue": 0,
        "scale_factor": 1.0,
        "add_offset": 0,
    }
    assert ds["x"].attrs == {
        "standard_name": "projection_x_coordinate",
        "long_name": "x coordinate of projection",
        "axis": "X",
        "units": "meters",
    }
    assert ds["y"].attrs == {
        "standard_name": "projection_y_coordinate",
        "long_name": "y coordinate of projection",
        "axis": "Y",
        "units": "meters",
    }
    assert ds["t"].attrs == {"standard_name": "time", "axis": "T"}


if __name__ == "__main__":
    pass
