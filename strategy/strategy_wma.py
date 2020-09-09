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
    df["last_signal"] = calcLastSignal(df, max(wma_period, ema_period))
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


def calcLastSignal(df, initialOffset):
    last_signal = [(np.nan, np.nan)] * len(df)
    last_buy, last_sell = 0, 0

    for i in range(initialOffset + 1, len(df)):
        if buy_signal_wma(df, i):
            last_buy = i
        elif sell_signal_wma(df, i):
            last_sell = i

        last_signal[i] = (last_buy, last_sell)

    return last_signal


def sell_or_buy(df, i, status):
    last_sign = "buy" if df["last_signal"][i][0] > df["last_signal"][i][1] else "sell"
    if status == 0 and last_sign == "buy":
        return "buy"
    elif status == 1 and last_sign == "sell":
        return "sell"
    else:
        return "hold"
