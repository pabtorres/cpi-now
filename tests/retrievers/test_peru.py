import pandas as pd
import pytest

from cpinow.names import CPIColumns
from cpinow.retrievers.peru import PeruCPIRetriever
from cpinow.schemas import CPI_SCHEMA

FIXTURE = "tests/data/peru.json"


class TestPeruRetriever:
    @pytest.fixture
    def retriever(self):
        return PeruCPIRetriever()

    def test_parse(self, retriever):
        data = retriever.parse(FIXTURE)
        CPI_SCHEMA.validate(data)

        # Leading "n.d." values are dropped: series starts on Jan 1991
        assert data[CPIColumns.DATE.value].min() == pd.Timestamp("1991-01-01")
        # Reference date extracted from "(índice Dic.2021 = 100)"
        assert (data[CPIColumns.REFERENCE_DATE.value] == pd.Timestamp("2021-12-01")).all()
        # Values rounded to the series' decimals, like cpilatam
        assert data[CPIColumns.CPI.value].iloc[0] == 7.39
        # Internal "n.d." gap (Jul 1991) is forward filled
        jun, jul = data.set_index(CPIColumns.DATE.value).loc[["1991-06-01", "1991-07-01"], CPIColumns.CPI.value]
        assert jun == jul
        assert data[CPIColumns.CPI.value].notna().all()

    def test_parse_period(self):
        assert PeruCPIRetriever._parse_period("Dic.2021") == pd.Timestamp("2021-12-01")
        assert PeruCPIRetriever._parse_period("Ene.1991") == pd.Timestamp("1991-01-01")
        with pytest.raises(ValueError):
            PeruCPIRetriever._parse_period("2021-12")

    def test_launch_with_failed_download_keeps_local_data(self, retriever, monkeypatch):
        before = retriever.data.copy()
        monkeypatch.setattr(retriever, "download", lambda: (None, True))
        retriever.launch()
        pd.testing.assert_frame_equal(before, retriever.data)

    def test_local_data(self, retriever):
        data = CPI_SCHEMA.validate(retriever.data)
        assert data[CPIColumns.DATE.value].is_monotonic_increasing
        assert data[CPIColumns.DATE.value].is_unique
        assert (data[CPIColumns.CPI.value] > 0).all()


def test_df_cpi_peru_key_is_case_insensitive():
    """``DF_CPI["peru"]`` (the cpilatam key) must keep working."""
    from cpinow import DF_CPI

    assert DF_CPI["peru"] is DF_CPI["Peru"]
    assert "peru" in DF_CPI
    assert set(DF_CPI["peru"].columns) == {c.value for c in CPIColumns}
