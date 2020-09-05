import numpy as np
from finta import TA


def get_strategy_name():
    return "supertrend"


def prep_data(df, multiplier=3, atr_period=50):
    multiplier = float(multiplier)
    atr_period = int(atr_period)

    df = df.copy()
    df["atr"] = TA.ATR(df, atr_period)
    df["up"] = df["open"] - (multiplier * df["atr"])
    df["up2"] = df["up"].bfill()
    df["dn"] = df["open"] + (multiplier * df["atr"])
    df["dn2"] = df["dn"].bfill()
    df["s_up"] = s_up(df)
    df["s_dn"] = s_dn(df)
    df["trend"] = get_trend(df)

    return df


def s_up(df):
    s_up = []
    s_up.append(df["up2"][0])
    for i in range(1, len(df)):
        if df["up2"][i] > s_up[-1] or df["close"][i - 1] < s_up[-1]:
            s_up.append(df["up2"][i])
        else:
            s_up.append(s_up[-1])
    return s_up


def s_dn(df):
    s_dn = []
    s_dn.append(df["dn2"][0])
    for i in range(1, len(df)):
        if df["dn2"][i] < s_dn[-1] or df["close"][i - 1] > s_dn[-1]:
            s_dn.append(df["dn2"][i])
        else:
            s_dn.append(s_dn[-1])
    return s_dn


def get_trend(df):
    trend = []
    trend.append(1)

    for i in range(1, len(df)):
        curr_trend = trend[-1]
        if trend[-1] == -1 and df["close"][i] > df["s_dn"][i]:
            curr_trend = 1
        elif trend[-1] == 1 and df["close"][i] < df["s_up"][i]:
            curr_trend = -1

        trend.append(curr_trend)

    return trend


def buy_signal_st(df, i):
    if i == 0:
        return False
    if df["trend"][i] == 1 and df["trend"][i - 1] == -1:
        return True
    else:
        return False


def sell_signal_st(df, i):
    if i == 0:
        return False
    if df["trend"][i] == -1 and df["trend"][i - 1] == 1:
        return True
    else:
        return False


def sell_or_buy(df, i, status):
    if status == 0 and buy_signal_st(df, i):
        return "buy"
    elif status == 1 and sell_signal_st(df, i):
        return "sell"
    else:
        return "hold"
