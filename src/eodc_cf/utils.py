"""Utility functions for applying CF metadata to xarray datasets."""

import xarray as xr

from eodc_cf._core import CFDataset


def assign_cf_metadata(ds: xr.Dataset, cf_ds: CFDataset) -> xr.Dataset:
    """Apply all CF attributes from cf_ds to ds."""
    ds.attrs.update(cf_ds.attrs)
    for var_name, cf_var in cf_ds.variables.items():
        ds[var_name].attrs.update(cf_var.attrs)
        for coord_name, cf_coord in cf_var.coordinates.items():
            ds[var_name][coord_name].attrs.update(cf_coord.attrs)

    return ds


if __name__ == "__main__":
    pass
