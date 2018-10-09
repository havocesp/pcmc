# PCMC

 - Author: Daniel J. Umpierez
 - License: MIT
 - Version: 0.1.2

## Description

CoinMarketCap Site Scrapper to Pandas Dataframes.

## Installation
### Using `pip` command

```sh
# `pip` command by supplying the github project repo URL.
$ pip install --process-dependencies-link git+https://github.com/havocesp/pcmc
```

## Usage

### CLI

```sh
# show accepted arguments
$ pcmc --help
# show 1H gainers filtered by exchanges HITBTC, BINANCE and CRYPTOPIA
$ pcmc --timeframe 1h --filter_by gainers hitbtc binance cryptopia
```

## Changelog

Project history changes.

### 0.1.2
 - Many function documentation added (with some "Doctests").
 - Added new function to handle cache data.
 - Screen clear on every update (useful for loop mode).

### 0.1.1

 - `pcmc` command added to easy run CLI interface from anywhere.
 - Loop flag and loop interval CLI args added for auto run mode.
 - New BTC price added (calculated from USD one at curren BTC ratio)

### 0.1.0

 - "All" page data.
 - "Gainers and Losers" page.
 
## TODO
 - [ ] Show diff between refreshes.
 - [x] Retrieve prices in BTC currency.
 - [x] CLI interface.
