import numpy as np
from finta import TA


def get_strategy_name():
    return "hma"


def prep_data(df, fast_period=12, slow_period=24):
    fast_period = int(fast_period)
    slow_period = int(slow_period)

    df = df.copy()
    df["hma_fast"] = TA.HMA(df, fast_period)
    df["hma_slow"] = TA.HMA(df, slow_period)
    return df


def buy_signal_hma(df, i):
    if i == 0:
        return False
    if (
        df["hma_fast"][i] >= df["hma_slow"][i]
        and df["hma_fast"][i - 1] < df["hma_slow"][i - 1]
    ):
        return True
    else:
        return False


def sell_signal_hma(df, i):
    if i == 0:
        return False
    if (
        df["hma_fast"][i] <= df["hma_slow"][i]
        and df["hma_fast"][i - 1] > df["hma_slow"][i - 1]
    ):
        return True
    else:
        return False


def sell_or_buy(df, i, status):
    if status == 0 and buy_signal_hma(df, i):
        return "buy"
    elif status == 1 and sell_signal_hma(df, i):
        return "sell"
    else:
        return "hold"

