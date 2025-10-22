import rioxarray as riox
import xarray as xr
from _core import CFDataset


def assign_cf_metadata(ds: xr.Dataset, cf_ds: CFDataset) -> xr.Dataset:
    ds.attrs.update(cf_ds.to_dict())
    for var_name, cf_var in cf_ds.variables.items():
        ds[var_name].attrs.update(cf_var.to_dict())
        for coord_name, cf_coord in cf_var.coordinates.items():
            ds[var_name][coord_name].attrs.update(cf_coord.to_dict())

    return ds


def create_ds_from_cf_metadata(cf_ds: CFDataset) -> xr.Dataset:
    pass


if __name__ == "__main__":
    from lib import CFXCoordinate, CFYCoordinate, CFTimeCoordinate, CFCoordinate
    from _core import CFDataVariable
    import numpy as np
    import datetime
    import pandas as pd
    import dask.array as da
    import rasterio
    
    ZARR_VERSION = 3
    S_CHUNKSIZE = 256
    T_CHUNKSIZE = 360
    N_TIMES = 360
    N_POLS = 2
    VAR_LABEL = 'sig0' 
    STD_NAME = 'gtc_sigma_nought_backscatter' 
    POL_LABEL = "polarisation"
    TIME_LABEL = 'local_time'
    X_LABEL = 'x'
    Y_LABEL = 'y'
    DC_DIMENSIONS = [POL_LABEL, TIME_LABEL, Y_LABEL, X_LABEL]
    SAMPLING = 20
    EU_BBOX = [0, 0, 8663040, 6021120]
    MAX_ZOOM = 10
    POLS = ["VV", "VH"]

    timestamps = np.array(pd.date_range(datetime.datetime(2018, 1, 1, 6), datetime.datetime(2018, 1, 1) + datetime.timedelta(days=N_TIMES//2), freq="12H",))
    ys = np.arange(EU_BBOX[3] - SAMPLING/2., EU_BBOX[1], -SAMPLING, dtype=np.int32)
    xs = np.arange(EU_BBOX[0] + SAMPLING/2., EU_BBOX[2], SAMPLING, dtype=np.int32)
    width, height = int(round((EU_BBOX[2] - EU_BBOX[0])/SAMPLING)), int(round((EU_BBOX[3] - EU_BBOX[1])/SAMPLING))
    empty_da = xr.DataArray(
        da.empty(
            shape=(N_POLS, N_TIMES, height, width),
            dtype=np.int16,
            chunks=(1, T_CHUNKSIZE, S_CHUNKSIZE, S_CHUNKSIZE),
        ),
        dims=DC_DIMENSIONS,
        coords={POL_LABEL: POLS,
                TIME_LABEL: timestamps,
                Y_LABEL: ys, 
                X_LABEL: xs}
    )
    empty_ds = empty_da.to_dataset(name=VAR_LABEL)
    empty_ds = empty_ds.rio.write_crs("epsg:27704")
    transform = rasterio.transform.from_bounds(*EU_BBOX, width, height)
    transform = transform.to_gdal()
    transform = " ".join([str(i) for i in transform])
    empty_ds["spatial_ref"].attrs["GeoTransform"] = transform


    cf_x = CFXCoordinate(name=X_LABEL)
    cf_y = CFYCoordinate(name=Y_LABEL)
    cf_t = CFTimeCoordinate(name=TIME_LABEL, units="days since 1990-1-1 0:0:0")
    cf_p = CFCoordinate(name=POL_LABEL, standard_name="polarisation")

    cf_sig0 = CFDataVariable(name="sig0", standard_name=STD_NAME, units="dB", scale_factor=0.1, fill_value=np.int16(-9999))
    cf_sig0 = cf_sig0 + cf_p + cf_t + cf_y + cf_x

    cf_ds = CFDataset([cf_sig0], title="SIG0", source="GRD") 
    empty_ds = assign_cf_metadata(empty_ds, cf_ds)
    pass
