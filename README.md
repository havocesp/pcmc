# PCMC

 - Author: Daniel J. Umpierrez
 - License: UNLICENSE
 - Version: 0.1.6

## Description

CoinMarketCap Site Scrapper to Pandas Dataframes.

## Installation
### Using `pip` command

```sh
# `pip` command by supplying the github project repo URL.
$ pip install git+https://github.com/havocesp/pcmc
```

## Usage

### CLI

```sh
# show accepted arguments
$ pcmc --help
# show 1H gainers filtered by exchanges HITBTC, BINANCE and CRYPTOPIA
$ pcmc --timeframe 1h --filter_by gainers hitbtc binance cryptopia
```

## Project dependencies.
 - [pandas](https://pypi.org/project/pandas/)
 - [py-term](https://pypi.org/project/py-term)

## Changelog

Project history changes.

### 0.1.6
 - New CoinMarketCap class on static.py
 - Some code tidy task accomplished and some typo fixing.

### 0.1.5
 - Added BeautifulSoap dependence for better scrapping.
 - Removed ccxt, AppDirs, requests, begins and tabulate dependencies.
 - Many new methods added to "CoinMarketCap" class
 - New 'static.py' module to serve as a global constants container.
 - Fixed error on losers 7d and 24h methods.

### 0.1.4
 - New rate extraction  from html code.
 - New "core" function `extract_rate` for html code rate extraction
 - `cryptocmp` dependency removed.
 - Some unused `CoinMarketCap` methods removed.
 - `__init__` file `__long_description__` error fixed.

### 0.1.3
 - New `utils.py` module containing `cli.py` functions helpers.

### 0.1.2
 - Many function documentation added (with some "Doctests").
 - Added new function to handle cache data.
 - Screen clear on every update (useful for loop mode).

### 0.1.1

 - `pcmc` command added to easy run CLI interface from anywhere.
 - Loop flag and loop interval CLI args added for auto run mode.
 - New BTC price added (calculated from USD one at current BTC ratio)

### 0.1.0

 - "All" page data.
 - "Gainers and Losers" page.
 
## TODO
 - [ ]
 - [ ] Get symbol list supported by an exchange.
 - [ ] Show diff between refreshes.
 - [x] Retrieve prices in BTC currency.
 - [x] CLI interface.
