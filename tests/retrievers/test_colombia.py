import pytest

from cpinow.retrievers.colombia import ColombiaCPIRetriever
from cpinow.schemas import CPI_SCHEMA


class TestColombiaRetriever:
    @pytest.fixture
    def setUp(self, monkeypatch):
        # crear instancia
        self.retriever = ColombiaCPIRetriever()

        # mock download using monkeypatch
        monkeypatch.setattr(self.retriever, "download", self.mock_download)

    def mock_download(self):
        return "tests/data/colombia.xlsx", False

    def test_retrieval(self, setUp):
        # read data
        path, error = self.retriever.download()

        # parse and validate the data
        CPI_SCHEMA.validate(self.retriever.parse(path))
