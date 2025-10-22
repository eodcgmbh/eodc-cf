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
    pass
