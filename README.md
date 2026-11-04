# cpi-now
[![PyPI version fury.io](https://badge.fury.io/py/cpinow.svg)](https://pypi.python.org/pypi/cpinow/)
[![PyPI download month](https://img.shields.io/pypi/dm/cpinow.svg)](https://pypi.python.org/pypi/cpinow/)
[![GitHub license](https://img.shields.io/github/license/pabtorres/cpi-now.svg)](https://github.com/pabtorres/cpi-now/blob/main/LICENSE)
[![Passing](https://github.com/pabtorres/cpi-now/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/pabtorres/cpi-now/actions/workflows/ci.yml)

`cpi-now` is a Python library designed to simplify the retrieval of Consumer Price Index (CPI) values from the central banks of countries, `cpi-now` is based on `cpi-latam` being a fork version that suits better for the usage of Selenium for data retrieval.


Available countries:
- Colombia 🇨🇴 — Banco de la República (Selenium).
- Perú 🇵🇪 — BCRP, series `PN38705PM` (IPC Lima Metropolitana, Dic.2021 = 100), via the BCRP statistics API.

## Installation
```python
pip install cpinow
```

## Develop & Contribute

### Locally
```bash
python -m venv .venv
poetry update
```

### Branch Protocol

- Create a feature branch, merge it to dev
- Merge dev to main
- Generate a Release branch vYYYY.MM.DD
```bash
git tag vYYYY.MM.DD
git push origin vYYYY.MM.DD
```


## Usage
```python
from cpinow import DF_CPI

# Retrieve CPI data for Colombia
print(DF_CPI["Colombia"])

# Retrieve CPI data for Peru (keys are case-insensitive, so DF_CPI["peru"] also works, as in cpilatam)
print(DF_CPI["Peru"])
```

### Migrating from `cpilatam`
`DF_CPI["peru"]` returns the same columns (`date`, `cpi`, `reference_date`) and values as `cpilatam`, so only the
import has to change:
```python
# from cpilatam import DF_CPI
from cpinow import DF_CPI

df_inflation = DF_CPI["peru"]
```
## Update CPI Data
Keep your CPI data up-to-date by using the following update function:
```python
from cpinow import update
update()           # all countries
update(["Peru"])   # only Peru (no Selenium/browser needed)
```
### Notes:
- Ensure you have an active internet connection for successful data retrieval.
- The library currently supports data from Colombia and Peru. Future updates may include additional countries.
- For the latest features and improvements, check the GitHub repository.
