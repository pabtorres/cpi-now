import pytest


def test_import():
    import cpinow  # noqa: F401


def test_dataframe_schemas():
    from cpinow import DF_CPI
    from cpinow.schemas import CPI_SCHEMA

    assert isinstance(DF_CPI, dict)
    for df in DF_CPI.values():
        CPI_SCHEMA.validate(df)


@pytest.mark.scrapping
def test_update():
    from cpinow import update

    update()
