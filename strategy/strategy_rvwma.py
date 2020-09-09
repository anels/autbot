import numpy as np
from finta import TA


def get_strategy_name():
    return "rvwma"


def rolling_vwma(df, rolling_period):
    cv = df["close"] * df["volume"]
    r_cv = cv.rolling(rolling_period).sum()
    r_v = df["volume"].rolling(rolling_period).sum()
    rvwma = (r_cv / r_v).bfill()
    return rvwma


def prep_data(df, rvwma_period=34, wma_period=21):
    rvwma_period = int(rvwma_period)
    wma_period = int(wma_period)

    df = df.copy()

    df["wma"] = TA.WMA(df, wma_period)
    df["rvwma"] = rolling_vwma(df, rvwma_period)
    df["last_signal"] = calcLastSignal(df, max(wma_period, rvwma_period))
    return df


def buy_signal_rvwma(df, i):
    if i == 0:
        return False
    if df["wma"][i] >= df["rvwma"][i] and df["wma"][i - 1] < df["rvwma"][i - 1]:
        return True
    else:
        return False


def sell_signal_rvwma(df, i):
    if i == 0:
        return False
    if df["wma"][i] <= df["rvwma"][i] and df["wma"][i - 1] > df["rvwma"][i - 1]:
        return True
    else:
        return False


def calcLastSignal(df, initialOffset):
    last_signal = [(np.nan, np.nan)] * len(df)
    last_buy, last_sell = 0, 0

    for i in range(initialOffset + 1, len(df)):
        if buy_signal_rvwma(df, i):
            last_buy = i
        elif sell_signal_rvwma(df, i):
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
