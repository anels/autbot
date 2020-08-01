# AuTBot (Auto Trading Bot)

This bot automatically retrives stock data from yahoo finance and using one of the strategy to decide buy or sell. If you config yoru robinhood account. It can automatically place order on robinhood.


## Installation

Step 1.
```
virtualenv .
```

Step 2.
```
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

## Test & Benchmark Strategies

Start jupyter notebook and run `strategy_benchmark`.



## Disclaimer
Use at your own risk. None of the authors or contributors, in any way whatsoever, can be responsible for your investment gain or loss by using of the software.
