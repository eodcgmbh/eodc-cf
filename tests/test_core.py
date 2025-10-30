from pydantic_core._pydantic_core import ValidationError

from eodc_cf._core import CFBase


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


if __name__ == "__main__":
    pass
