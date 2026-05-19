"""Tests for the soft-deprecation of the CFMultiscale* family.

The CFMultiscale{Layout,Attributes,Dataset} models predate and are incompatible
with the GeoZarr `multiscales` convention (different UUID, different attribute
names, no JSON Schema).  They are kept importable for backwards compatibility
but emit a ``DeprecationWarning`` at instantiation time.

See the project's GeoZarr stack review for the migration recipe to
``zarr-cm`` / ``geozarr-toolkit``.
"""

import warnings

import pytest

from eodc_cf import (
    CFMultiscaleAttributes,
    CFMultiscaleDataset,
    CFMultiscaleLayout,
)


def test_cf_multiscale_layout_warns_on_instantiation():
    with pytest.warns(DeprecationWarning, match="GeoZarr"):
        CFMultiscaleLayout(id="L0", cell_size=(1.0, 1.0))


def test_cf_multiscale_attributes_warns_on_instantiation():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        layout = CFMultiscaleLayout(id="L0", cell_size=(1.0, 1.0))
    with pytest.warns(DeprecationWarning, match="GeoZarr"):
        CFMultiscaleAttributes(layout=[layout])


def test_cf_multiscale_dataset_warns_on_instantiation():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        layout = CFMultiscaleLayout(id="L0", cell_size=(1.0, 1.0))
        attrs = CFMultiscaleAttributes(layout=[layout])
    with pytest.warns(DeprecationWarning, match="GeoZarr"):
        CFMultiscaleDataset(title="ds", source="src", multiscales=attrs)


def test_importing_eodc_cf_does_not_warn():
    """The warning should only fire on *instantiation* of the deprecated classes."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        import eodc_cf  # noqa: F401  re-import is fine; importing must not warn
