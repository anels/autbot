# AuTBot (Auto Trading Bot)

This bot automatically retrieves stock data from yahoo finance and using one of the strategy to decide buy or sell. If you config your robinhood account. It can automatically place order on robinhood.

## Download

Please go to Release section to get the latest release or clone this repo.

## Installation

Step 1.

Download the latest release from release tab or clone this repo.

Step 2. (Optional)

```
virtualenv .
Scripts\activate
```

Step 3.

```
pip install -r requirements.txt
```

## Configuration

Copy two files in the `sample_config` folder and modify them according to your needs

## Run Program

```
autbot.py -a <account_info_file> -c <config_file>
```

or

```
main_runner.py "autbot.py -a <account_info_file> -c <config_file>"
```

`main_runner.py` will auto-restart your bot if it stops.

## Test & Benchmark Strategies

Start jupyter notebook and run `strategy_benchmark.ipynb`.

## Recap Trade History

Start jupyter notebook and run `recap.ipynb`.

## Disclaimer

Use at your own risk. None of the authors or contributors, in any way whatsoever, can be responsible for your investment gain or loss by using of the software.
