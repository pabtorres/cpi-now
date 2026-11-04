"""CPI retriever for Peru.

Based on ``cpilatam.parsers.peru.PeruCPIParser`` (https://github.com/stgoa/cpi-latam): same source series
(BCRP ``PN38705PM`` - Índice de precios Lima Metropolitana, IPC) and same output (values rounded to the
series' published decimals, reference date taken from the series name). Instead of scraping the HTML table
it uses the official BCRP statistics JSON API, which serves the very same series.
"""

import json
import re
from datetime import date
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import requests

from cpinow import SETTINGS, logger
from cpinow.names import Countries, CPIColumns
from cpinow.schemas import CPI_SCHEMA


class PeruCPIRetriever:
    """CPI Retriever for Peru using the BCRP statistics API."""

    SERIES_CODE = "PN38705PM"
    BASE_URL = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{series}/json/{start}/{end}"
    START_DATE = date(1991, 1, 1)

    MONTH_MAP = {
        "Ene": 1,
        "Feb": 2,
        "Mar": 3,
        "Abr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Ago": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dic": 12,
    }
    MONTH_PATTERN = r"(Ene|Feb|Mar|Abr|May|Jun|Jul|Ago|Sep|Oct|Nov|Dic)\.?(\d{4})"

    def __init__(self, timeout: int = 30):
        today = date.today()
        self.site = self.BASE_URL.format(
            series=self.SERIES_CODE,
            start=f"{self.START_DATE.year}-{self.START_DATE.month}",
            end=f"{today.year}-{today.month}",
        )
        self.timeout = timeout
        self.local_file_path = SETTINGS.PERU_LOCAL_PATH
        self.attempts = 3
        self.country = Countries.PERU.value
        self.data = pd.read_csv(self.local_file_path.as_posix())

    def launch(self):
        """Launches the retriever: downloads, parses, validates and saves the CPI data."""
        logger.info("Launching Peru CPI Retriever.")
        payload, error = None, True

        while error and self.attempts > 0:
            payload, error = self.download()
            self.attempts -= 1

        if error:
            logger.error("Failed to download Peru CPI data after multiple attempts.")
            logger.info("Using the last downloaded file.")
            return None
        logger.info("Peru CPI data downloaded successfully.")

        self.save(self.parse(payload), self.local_file_path)
        self.data = pd.read_csv(self.local_file_path.as_posix())

    def download(self) -> Tuple[Optional[dict], bool]:
        """Requests the series to the BCRP API.

        Returns:
            Tuple with the JSON payload (``None`` on failure) and an error flag.
        """
        logger.info(f"Downloading Peru CPI data from {self.site}")
        try:
            response = requests.get(self.site, timeout=self.timeout)
            response.raise_for_status()
            return response.json(), False
        except (requests.RequestException, ValueError) as exc:
            logger.warning(f"Error downloading Peru CPI data: {exc}")
            return None, True

    @classmethod
    def _parse_period(cls, period: str) -> pd.Timestamp:
        """Converts a BCRP period (e.g. ``"Dic.2021"``) into the first day of that month."""
        match = re.fullmatch(cls.MONTH_PATTERN, period.strip())
        if match is None:
            raise ValueError(f"Unexpected period format: {period!r}")
        return pd.Timestamp(year=int(match.group(2)), month=cls.MONTH_MAP[match.group(1)], day=1)

    @classmethod
    def _parse_reference_date(cls, series_name: str) -> pd.Timestamp:
        """Extracts the base date from the series name, e.g. ``"(índice Dic.2021 = 100)"``."""
        match = re.search(cls.MONTH_PATTERN, series_name)
        if match is None:
            raise ValueError(f"Reference date not found in series name: {series_name!r}")
        return pd.Timestamp(year=int(match.group(2)), month=cls.MONTH_MAP[match.group(1)], day=1)

    def parse(self, payload) -> pd.DataFrame:
        """Parses the BCRP API payload into the universal CPI schema.

        Args:
            payload: The decoded JSON (dict) or a path to a JSON file with it.

        Returns:
            DataFrame with ``date``, ``cpi`` and ``reference_date`` columns.
        """
        if isinstance(payload, (str, Path)):
            with open(payload, encoding="utf-8") as file:
                payload = json.load(file)

        series = payload["config"]["series"][0]
        decimals = int(series.get("dec", 2))
        reference_date = self._parse_reference_date(series["name"])

        data = pd.DataFrame(
            {
                CPIColumns.DATE.value: [self._parse_period(p["name"]) for p in payload["periods"]],
                CPIColumns.CPI.value: [p["values"][0] for p in payload["periods"]],
            }
        )
        # "n.d." (no data) and other non numeric values become NaN
        data[CPIColumns.CPI.value] = pd.to_numeric(data[CPIColumns.CPI.value], errors="coerce")

        # Keep the range between the first and last available values and fill internal gaps
        first = data[CPIColumns.CPI.value].first_valid_index()
        last = data[CPIColumns.CPI.value].last_valid_index()
        if first is None:
            raise ValueError("The Peru CPI series has no values.")
        data = data.loc[first:last].reset_index(drop=True)
        data[CPIColumns.CPI.value] = data[CPIColumns.CPI.value].ffill().round(decimals)

        data[CPIColumns.REFERENCE_DATE.value] = reference_date

        return CPI_SCHEMA.validate(data)

    def save(self, data: pd.DataFrame, file_path) -> Path:
        """Saves parsed data to CSV."""
        data.to_csv(file_path, index=False, date_format="%Y-%m-%d")
        logger.info(f"Data saved to {file_path}")
        return file_path


if __name__ == "__main__":
    retriever = PeruCPIRetriever()
    retriever.launch()
    print(retriever.data.tail())
