# eodc-cf

Generic and light-weight package to assist CF-compliant dataset creation.

> **GeoZarr note.** `eodc-cf` is a **CF-conventions** helper. It does *not*
> implement the [GeoZarr](https://geozarr.org) conventions (`geo-proj`,
> `spatial`, `multiscales`). The `CFMultiscale{Layout,Attributes,Dataset}`
> models in this package predate and are **incompatible** with the
> GeoZarr `multiscales` convention (different UUID, different attribute
> names, no JSON Schema). They are kept importable for backwards
> compatibility but emit a `DeprecationWarning` on instantiation and will
> be removed in a future release.
>
> For spec-compliant GeoZarr metadata use
> [`zarr-cm`](https://github.com/zarr-conventions/zarr-cm) (primitives,
> zero-dep) or [`geozarr-toolkit`](https://github.com/zarr-developers/geozarr-toolkit)
> (Pydantic models + CLI). The CF helpers in this package remain useful
> for variable-level CF metadata (`standard_name`, `_FillValue`, etc.) and
> are *complementary* to GeoZarr.

# Installation

```bash
pip install git+https://github.com/eodcgmbh/eodc-cf.git
```

## Usage and examples

_eodc-cf_ contains all user-facing classes at its root and a `utils` module, which collects some useful helper functions. 

### Coordinates
In terms of multi-dimensional dataset hierarchy, the `CFCoordinate` class is at the lowest level. It defines some mandatory attributes like `name` and `standard_name`, and optional attributes like `long_name` or `units`. Certain attribute values are validated during class initialisation to ensure that they are CF compliant, e.g., `axis` always needs to have a single uppercase letter.


```python
from pprint import pprint
from eodc_cf import CFCoordinate

cf_coord = CFCoordinate(name="z", standard_name="z_coordinate", axis="Z", units="m")
```

Besides directly accessing the class attributes, `CFCoordinate` has the `attrs` property, which allows to retrieve CF compliant metadata attributes as a dictionary.


```python
pprint(cf_coord.attrs)
```

    {'axis': 'Z', 'standard_name': 'z_coordinate', 'units': 'm'}


There are already some pre-defined coordinate classes available, e.g., `CFXCoordinate`, `CFYCoordinate`, `CFLonCoordinate`, `CFLatCoordinate`, and `CFTimeCoordinate`.


```python
from eodc_cf import CFXCoordinate

cf_xcoord = CFXCoordinate(name="x")
pprint(cf_xcoord.attrs)
```

    {'axis': 'X',
     'long_name': 'x coordinate of projection',
     'standard_name': 'projection_x_coordinate',
     'units': 'meters'}


### Data variables
There are two types of data variables, `CFDataVariable` and `CFFlagVariable`. `CFDataVariable` defines (CF) attributes for data variables representing a physical quantity and `CFFlagVariable` for boolean or bitwise data flags. Here is an example with `CFDataVariable`:


```python
from eodc_cf import CFDataVariable

cf_dvar = CFDataVariable(
        name="dem", 
        standard_name="digital_elevation_model", 
        scale_factor=2.0, 
        add_offset=0,
        fill_value=-9999, 
        units="m",
    )
pprint(cf_dvar.attrs)
```

    {'_FillValue': -9999,
     'add_offset': 0,
     'scale_factor': 2.0,
     'standard_name': 'digital_elevation_model',
     'units': 'm'}


and here with `CFFlagVariable`:


```python
from eodc_cf import CFFlagVariable

cf_fvar = CFFlagVariable(
        name="qflag",
        standard_name="quality_flag",
        flag_values=[1 << 0, 1 << 1, 1 << 2],
        flag_meanings=[
            "processing_successfull",
            "retrieval_successful",
            "quality_good",
        ],
    )
pprint(cf_fvar.attrs)
```

    {'_FillValue': 255,
     'flag_meanings': 'processing_successfull retrieval_successful quality_good',
     'flag_values': [1, 2, 4],
     'standard_name': 'quality_flag'}


Each data variable can hold a set of coordinates with unique names. Coordinates can be attached to a data variable either during initialisation or at a later stage. Below is an example:


```python
from eodc_cf import CFXCoordinate, CFYCoordinate, CFTimeCoordinate

cf_xcoord = CFXCoordinate(name="x")
cf_ycoord = CFYCoordinate(name="y")
cf_dvar = CFDataVariable(
        name="temp", 
        standard_name="temperature", 
        fill_value=-9999, 
        units="degrees_celsius",
        cf_coords=[cf_xcoord, cf_ycoord]
    )
print(len(cf_dvar))
pprint(cf_dvar.coordinates)
```

    2
    {'x': CFXCoordinate(name='x', standard_name='projection_x_coordinate', long_name='x coordinate of projection', axis='X', units='meters'),
     'y': CFYCoordinate(name='y', standard_name='projection_y_coordinate', long_name='y coordinate of projection', axis='Y', units='meters')}



```python
cf_tcoord = CFTimeCoordinate(name="t", units="days since 1990-1-1 0:0:0")
cf_dvar = cf_dvar + cf_tcoord
print(len(cf_dvar))
pprint(cf_dvar.coordinates)
```

    3
    {'t': CFTimeCoordinate(name='t', standard_name='time', long_name=None, axis='T', units='days since 1990-1-1 0:0:0'),
     'x': CFXCoordinate(name='x', standard_name='projection_x_coordinate', long_name='x coordinate of projection', axis='X', units='meters'),
     'y': CFYCoordinate(name='y', standard_name='projection_y_coordinate', long_name='y coordinate of projection', axis='Y', units='meters')}


**Attention**: be aware that the `+` operator overwrites the initial instance!

### Dataset

The `CFDataset` is at the highest level of a multi-dimensional dataset hierarchy. It has some mandatory global attributes like `title` and `source` and can store several CF data variables.


```python
from eodc_cf import CFDataset

cf_ds = CFDataset(title="my dataset", source="my dataset source", cf_vars=[cf_dvar])
print(len(cf_ds))
pprint(cf_ds.attrs)
```

    1
    {'institution': 'EODC', 'source': 'my dataset source', 'title': 'my dataset'}


Also here we can now append CF data variables as we like:


```python
cf_ds = cf_ds + cf_fvar
print(len(cf_ds))
pprint(cf_ds.variables)
```

    2
    {'qflag': CFFlagVariable(name='qflag', standard_name='quality_flag', long_name=None, fill_value=255, valid_range=None, grid_mapping=None, other_attrs={}, flag_values=[1, 2, 4], flag_masks=None, flag_meanings=['processing_successfull', 'retrieval_successful', 'quality_good']),
     'temp': CFDataVariable(name='temp', standard_name='temperature', long_name=None, fill_value=-9999, valid_range=None, grid_mapping=None, other_attrs={}, scale_factor=1.0, add_offset=0, units='degrees_celsius')}


It is also possible to combine two datasets and join their variables:


```python
cf_ds1 = CFDataset(title="dataset1", source="source1", cf_vars=[cf_dvar])
cf_ds2 = CFDataset(title="dataset2", source="source2", cf_vars=[cf_fvar])
cf_ds1 = cf_ds1 + cf_ds2
pprint(cf_ds1.variables)
```

    {'qflag': CFFlagVariable(name='qflag', standard_name='quality_flag', long_name=None, fill_value=255, valid_range=None, grid_mapping=None, other_attrs={}, flag_values=[1, 2, 4], flag_masks=None, flag_meanings=['processing_successfull', 'retrieval_successful', 'quality_good']),
     'temp': CFDataVariable(name='temp', standard_name='temperature', long_name=None, fill_value=-9999, valid_range=None, grid_mapping=None, other_attrs={}, scale_factor=1.0, add_offset=0, units='degrees_celsius')}


### Multiscale dataset

An extension of the `CFDataset` is the `CFMultiscaleDataset`, which pre-defines the expected attributes to represent an "image pyramid"-like structure of the dataset. Each pyramid level is called a "layout" and is defined via the `CFMultiscaleLayout` class. 


```python
from eodc_cf import CFMultiscaleLayout

cf_ms_l0 = CFMultiscaleLayout(id="L0", cell_size=(1, 1))
pprint(cf_ms_l0)
```

    CFMultiscaleLayout(id='L0', cell_size=(1.0, 1.0), path=None, derived_from=None, factors=None, resampling_method=None)


`CFMultiscaleAttributes` then allows to define a set of layouts and some relevant metadata:


```python
from eodc_cf import CFMultiscaleAttributes

cf_ms_attrs = CFMultiscaleAttributes(
    layout=[cf_ms_l0], resampling_method="nearest"
)
pprint(cf_ms_attrs)
```

    CFMultiscaleAttributes(layout=[CFMultiscaleLayout(id='L0', cell_size=(1.0, 1.0), path=None, derived_from=None, factors=None, resampling_method=None)], version='1.0', tile_matrix_ref=None, resampling_method='nearest', overview_variables=None)


Also with `CFMultiscaleAttributes`, more multiscale layouts/layers can be added on-the-fly:


```python
cf_ms_l1 = CFMultiscaleLayout(id="L1", cell_size=(2, 2))
cf_ms_l2 = CFMultiscaleLayout(id="L2", cell_size=(4, 4))
cf_ms_attrs = cf_ms_attrs + cf_ms_l1 + cf_ms_l2
print(len(cf_ms_attrs))
```

    3


Finally, the `CFMultiscaleAttributes` instance can be attached to the `CFMultiscaleDataset` class. This class has then the same properties as a common `CFDataset` with a `multiscales` attribute on top.


```python
from eodc_cf import CFMultiscaleDataset

cf_ms_ds = CFMultiscaleDataset(title="multiscale dataset", source="my source", multiscales=cf_ms_attrs)
pprint(cf_ms_ds.attrs)
```

    {'institution': 'EODC',
     'multiscales': {'layout': [{'cell_size': (1.0, 1.0), 'id': 'L0'},
                                {'cell_size': (2.0, 2.0), 'id': 'L1'},
                                {'cell_size': (4.0, 4.0), 'id': 'L2'}],
                     'resampling_method': 'nearest',
                     'version': '1.0'},
     'source': 'my source',
     'title': 'multiscale dataset'}


# Testing

```bash
cd eodc-cf
pytest
```

# Contributing 

For implementing new features, or fixing bugs, we recommend to open a new branch from `develop` (or fork the repo). Upon completion, open a PR from the feature branch to `develop`, which allows the maintainers/owners to review your changes. 
