import numpy as np
from finta import TA


def get_strategy_name():
    return "wma"


def prep_data(df, wma_period=13, ema_period=13):
    wma_period = int(wma_period)
    ema_period = int(ema_period)

    df = df.copy()
    df.loc[:, "wma"] = TA.WMA(df, wma_period, "close")
    df.loc[:, "ema"] = TA.EMA(df, ema_period, "close")
    return df


def buy_signal_wma(df, i):
    if i == 0:
        return False
    if df["wma"][i] >= df["ema"][i] and df["wma"][i - 1] > df["ema"][i - 1]:
        return True
    else:
        return False


def sell_signal_wma(df, i):
    if i == 0:
        return False
    if df["wma"][i] < df["ema"][i] and df["wma"][i - 1] >= df["ema"][i - 1]:
        return True
    else:
        return False


def sell_or_buy(df, i, status):
    if status == 0 and buy_signal_wma(df, i):
        return "buy"
    elif status == 1 and sell_signal_wma(df, i):
        return "sell"
    else:
        return "hold"
