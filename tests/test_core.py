from pydantic_core._pydantic_core import ValidationError

from eodc_cf._core import (
    CFBase,
    CFCoordinate,
    CFDataset,
    CFDataVariable,
    CFDataVariableBase,
    CFFlagVariable,
    CFMultiscaleAttributes,
    CFMultiscaleDataset,
    CFMultiscaleLayout,
)


def test_cf_base():
    cf_base = CFBase(name="var", standard_name="var_name")
    assert cf_base.model_dump() == {
        "name": "var",
        "standard_name": "var_name",
        "long_name": None,
    }

    try:
        cf_base = CFBase(name="Var", standard_name="var_name")
        raise AssertionError()
    except Exception as e:
        assert str(e) == "String 'Var' does not comply with the CF naming convention."

    try:
        cf_base = CFBase(name="var")
        raise AssertionError()
    except ValidationError:
        assert True

    try:
        cf_base = CFBase(name="var", standard_name="var_name", long_name=123)
        raise AssertionError()
    except ValidationError:
        assert True


def test_cf_coordinate():
    cf_coord = CFCoordinate(name="z", standard_name="z_coordinate", axis="Z", units="m")
    assert cf_coord.model_dump() == {
        "name": "z",
        "standard_name": "z_coordinate",
        "long_name": None,
        "axis": "Z",
        "units": "m",
    }

    try:
        cf_coord = CFCoordinate(
            name="z", standard_name="z_coordinate", axis="z", units="m"
        )
        raise AssertionError()
    except Exception as e:
        assert str(e) == "Axis name 'z' does not comply with the CF naming convention."

    cf_coord = CFCoordinate(name="z", standard_name="z_coordinate", axis="Z")
    assert cf_coord.attrs == {
        "standard_name": "z_coordinate",
        "axis": "Z",
    }


def test_cf_datavar_base():
    cf_dvar = CFDataVariableBase(
        name="var",
        standard_name="var_name",
        fill_value=99,
        valid_range=(2, 9.5),
        grid_mapping="spatial_ref",
    )
    assert cf_dvar.model_dump() == {
        "name": "var",
        "standard_name": "var_name",
        "long_name": None,
        "fill_value": 99,
        "valid_range": (2, 9.5),
        "grid_mapping": "spatial_ref",
        "other_attrs": {},
    }
    assert cf_dvar.attrs == {
        "standard_name": "var_name",
        "_FillValue": 99,
        "valid_range": (2, 9.5),
        "grid_mapping": "spatial_ref",
    }

    try:
        cf_dvar = CFDataVariableBase(
            name="var", standard_name="var_name", valid_range=(2, "s")
        )
        raise AssertionError()
    except ValidationError:
        assert True

    try:
        cf_dvar = CFDataVariableBase(
            name="var", standard_name="var_name", grid_mapping="SPATIAL_REF"
        )
        raise AssertionError()
    except Exception as e:
        assert (
            str(e)
            == "String 'SPATIAL_REF' does not comply with the CF naming convention."
        )

    try:
        cf_dvar = CFDataVariableBase(
            name="var", standard_name="var_name", other_attrs={"TEST": 123}
        )
        raise AssertionError()
    except Exception as e:
        assert str(e) == "String 'TEST' does not comply with the CF naming convention."

    cf_dvar = CFDataVariableBase(
        name="var", standard_name="var_name", other_attrs={"test": 123}
    )
    assert cf_dvar.attrs == {"standard_name": "var_name", "_FillValue": 0, "test": 123}


def test_cf_datavar():
    cf_dvar = CFDataVariable(
        name="var", standard_name="var_name", scale_factor=2.0, add_offset=1
    )
    assert cf_dvar.model_dump() == {
        "name": "var",
        "standard_name": "var_name",
        "long_name": None,
        "fill_value": 0,
        "scale_factor": 2,
        "add_offset": 1,
        "valid_range": None,
        "grid_mapping": None,
        "other_attrs": {},
        "units": None,
    }
    assert cf_dvar.attrs == {
        "standard_name": "var_name",
        "_FillValue": 0,
        "scale_factor": 2,
        "add_offset": 1,
    }


def test_cf_flagvar():
    cf_fvar = CFFlagVariable(
        name="flag",
        standard_name="flag_name",
        flag_values=[1 << 0, 1 << 1, 1 << 2],
        flag_meanings=[
            "processing_successfull",
            "retrieval_successful",
            "quality_good",
        ],
    )
    assert cf_fvar.model_dump() == {
        "name": "flag",
        "standard_name": "flag_name",
        "long_name": None,
        "fill_value": 255,
        "valid_range": None,
        "grid_mapping": None,
        "other_attrs": {},
        "flag_values": [1, 2, 4],
        "flag_meanings": [
            "processing_successfull",
            "retrieval_successful",
            "quality_good",
        ],
        "flag_masks": None,
    }
    assert cf_fvar.attrs == {
        "standard_name": "flag_name",
        "_FillValue": 255,
        "flag_values": [1, 2, 4],
        "flag_meanings": "processing_successfull retrieval_successful quality_good",
    }


def test_cf_dataset():
    cf_ds = CFDataset(title="dataset", source="source")
    assert cf_ds.model_dump() == {
        "title": "dataset",
        "source": "source",
        "institution": "EODC",
        "history": None,
        "references": None,
        "comment": None,
        "other_attrs": {},
    }
    assert cf_ds.attrs == {
        "title": "dataset",
        "source": "source",
        "institution": "EODC",
    }


def test_add_coords():
    cf_coord = CFCoordinate(name="x", standard_name="x_coordinate")
    cf_dvar = CFDataVariableBase(name="var", standard_name="var_name", cf_coords=[1])
    assert len(cf_dvar) == 0
    cf_dvar = CFDataVariableBase(
        name="var", standard_name="var_name", cf_coords=[cf_coord]
    )
    assert len(cf_dvar) == 1
    cf_dvar = cf_dvar + cf_coord
    assert len(cf_dvar) == 1
    cf_dvar2 = CFDataVariableBase(name="var", standard_name="var_name")
    cf_dvar2 = cf_dvar2 + 1 + "s" + cf_coord
    assert cf_dvar.coordinates == cf_dvar2.coordinates

    assert cf_dvar.attrs == {"standard_name": "var_name", "_FillValue": 0}


def test_add_vars():
    cf_coord = CFCoordinate(name="x", standard_name="x_coordinate")
    cf_dvar = CFDataVariable(name="var", standard_name="var_name")
    cf_dvar = cf_dvar + cf_coord

    cf_ds = CFDataset(title="dataset", source="source", cf_vars=[1])
    assert len(cf_ds) == 0
    cf_ds = CFDataset(title="dataset", source="source", cf_vars=[cf_dvar])
    assert len(cf_ds) == 1
    cf_ds = cf_ds + cf_dvar
    assert len(cf_ds) == 1
    cf_ds2 = CFDataset(
        title="dataset2",
        source="source",
    )
    cf_ds2 = cf_ds2 + 1 + "s" + cf_dvar
    assert cf_ds.variables == cf_ds2.variables


def test_combine_cf_ds():
    cf_dvar = CFDataVariable(name="var", standard_name="var_name")
    cf_fvar = CFFlagVariable(
        name="flag",
        standard_name="flag_name",
        flag_values=[1 << 0, 1 << 1, 1 << 2],
        flag_meanings=[
            "processing_successfull",
            "retrieval_successful",
            "quality_good",
        ],
    )

    cf_ds1 = CFDataset(title="dataset1", source="source1", cf_vars=[cf_dvar])
    cf_ds2 = CFDataset(title="dataset2", source="source2") + cf_fvar
    assert len(cf_ds1) == len(cf_ds2)
    n_vars = len(cf_ds1) + len(cf_ds2)
    cf_ds1 = cf_ds1 + cf_ds2
    assert len(cf_ds1) == n_vars


def test_cf_ms_layout():
    cf_ms_layout = CFMultiscaleLayout(id="L0", cell_size=(1, 1))
    assert cf_ms_layout.model_dump() == {
        "id": "L0",
        "cell_size": (1.0, 1.0),
        "path": None,
        "derived_from": None,
        "resampling_method": None,
        "factors": None,
    }


def test_cf_ms_attrs():
    cf_ms_layout1 = CFMultiscaleLayout(id="L0", cell_size=(1, 1))
    cf_ms_layout2 = CFMultiscaleLayout(id="L1", cell_size=(2, 2))
    cf_ms_layout3 = CFMultiscaleLayout(
        id="L2", cell_size=(4, 4), resampling_method="average"
    )
    cf_ms_attrs = CFMultiscaleAttributes(
        layout=[cf_ms_layout1], resampling_method="nearest"
    )

    assert cf_ms_attrs.model_dump() == {
        "layout": [
            {
                "id": "L0",
                "cell_size": (1.0, 1.0),
                "path": None,
                "derived_from": None,
                "resampling_method": None,
                "factors": None,
            }
        ],
        "version": "1.0",
        "tile_matrix_ref": None,
        "resampling_method": "nearest",
        "overview_variables": None,
    }

    assert len(cf_ms_attrs) == 1
    cf_ms_attrs = cf_ms_attrs + cf_ms_layout1
    assert len(cf_ms_attrs) == 1
    cf_ms_attrs = cf_ms_attrs + cf_ms_layout2
    assert len(cf_ms_attrs) == 2
    cf_ms_attrs = cf_ms_attrs + cf_ms_layout3
    assert len(cf_ms_attrs) == 2


def test_cf_ms_ds():
    cf_ms_layout1 = CFMultiscaleLayout(id="L0", cell_size=(1, 1))
    cf_ms_attrs = CFMultiscaleAttributes(
        layout=[cf_ms_layout1], resampling_method="nearest"
    )
    cf_ms_ds = CFMultiscaleDataset(
        title="msdataset", source="source", multiscales=cf_ms_attrs
    )
    assert cf_ms_ds.model_dump() == {
        "title": "msdataset",
        "source": "source",
        "institution": "EODC",
        "history": None,
        "references": None,
        "comment": None,
        "other_attrs": {},
        "multiscales": {
            "layout": [
                {
                    "id": "L0",
                    "cell_size": (1.0, 1.0),
                    "path": None,
                    "derived_from": None,
                    "resampling_method": None,
                    "factors": None,
                }
            ],
            "version": "1.0",
            "tile_matrix_ref": None,
            "resampling_method": "nearest",
            "overview_variables": None,
        },
    }
    assert cf_ms_ds.attrs == {
        "title": "msdataset",
        "source": "source",
        "institution": "EODC",
        "multiscales": {
            "layout": [
                {
                    "id": "L0",
                    "cell_size": (1.0, 1.0),
                }
            ],
            "version": "1.0",
            "resampling_method": "nearest",
        },
    }


if __name__ == "__main__":
    test_cf_ms_ds()
