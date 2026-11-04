# -*- coding: utf-8 -*-
"""Top level package for recursiveseriation"""

import pandas as pd

from cpinow.logger import configure_logging
from cpinow.names import Countries, CPIColumns
from cpinow.settings import init_settings

__app_name__ = "cpinow"
__version__ = "2026.11.4"

SETTINGS = init_settings()
logger = configure_logging(__app_name__ + " - v" + __version__, SETTINGS, kidnap_loggers=True)


class CPIDict(dict):
    """Dictionary of CPI dataframes with case-insensitive country keys.

    Allows ``DF_CPI["Peru"]`` as well as ``DF_CPI["peru"]`` (the key used by ``cpilatam``), so projects
    migrating from ``cpilatam`` only need to change the import.
    """

    def _resolve(self, key):
        if isinstance(key, str) and not super().__contains__(key):
            for existing in self.keys():
                if isinstance(existing, str) and existing.lower() == key.lower():
                    return existing
        return key

    def __getitem__(self, key):
        return super().__getitem__(self._resolve(key))

    def __setitem__(self, key, value):
        super().__setitem__(self._resolve(key), value)

    def __contains__(self, key):
        return super().__contains__(self._resolve(key))

    def get(self, key, default=None):
        return super().get(self._resolve(key), default)


DF_CPI = CPIDict(
    {
        Countries.COLOMBIA.value: pd.read_csv(SETTINGS.COLOMBIA_LOCAL_PATH.as_posix()),
        Countries.PERU.value: pd.read_csv(SETTINGS.PERU_LOCAL_PATH.as_posix()),
    }
)

for key, item in DF_CPI.items():
    if item[CPIColumns.DATE.value].max() <= pd.to_datetime("today").strftime("%Y-%m-%d"):
        logger.warn(f"The data is not up to date in the {key} country. Please run the update script.")


def update(countries: list = None):
    from cpinow.retrievers import __retrievers__

    if countries is None:
        countries = DF_CPI.keys()
    countries = {country.lower() for country in countries}
    for retriever in __retrievers__:
        if retriever.country.lower() in countries:
            logger.info(f"Updating {retriever.country} data...")
            retriever.launch()
            # replace the dataframe in the DF_CPI dictionary
            DF_CPI[retriever.country] = retriever.data
