# cpi-now
[![PyPI version fury.io](https://badge.fury.io/py/cpinow.svg)](https://pypi.python.org/pypi/cpinow/)
[![PyPI download month](https://img.shields.io/pypi/dm/cpinow.svg)](https://pypi.python.org/pypi/cpinow/)
[![GitHub license](https://img.shields.io/github/license/pabtorres/cpi-now.svg)](https://github.com/pabtorres/cpi-now/blob/main/LICENSE)
[![Passing](https://github.com/pabtorres/cpi-now/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/pabtorres/cpi-now/actions/workflows/ci.yml)

`cpi-now` is a Python library designed to simplify the retrieval of Consumer Price Index (CPI) values from the central banks of countries, `cpi-now` is based on `cpi-latam` being a fork version that suits better for the usage of Selenium for data retrieval.


Available countries:
- Colombia 🇨🇴

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
```
## Update CPI Data
Keep your CPI data up-to-date by using the following update function:
```python
from cpinow import update
update()
```
### Notes:
- Ensure you have an active internet connection for successful data retrieval.
- The library is currently designed to support data from Colombia only. Future updates may include additional countries.
- For the latest features and improvements, check the GitHub repository.
