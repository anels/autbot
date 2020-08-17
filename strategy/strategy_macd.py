import numpy as np
from finta import TA


def prep_data(df, fast_period=12, slow_period=24):
    if fast_period > slow_period:
        fast_period = slow_period

    shortEMA = df['close'].ewm(span=fast_period, adjust=False).mean()
    longEMA = df['close'].ewm(span=slow_period, adjust=False).mean()

    MACD = shortEMA - longEMA
    signal = MACD.ewm(span=9, adjust=False).mean()
    df['MACD'] = MACD
    df['Signal'] = signal
    return df


def buy_signal_macd(df, i):
    if i == 0:
        return False
    if df['MACD'][i] >= df['Signal'][i] and df['MACD'][i-1] < df['Signal'][i-1]:
        return True
    else:
        return False


def sell_signal_macd(df, i):
    if i == 0:
        return False
    if df['MACD'][i] <= df['Signal'][i] and df['MACD'][i-1] > df['Signal'][i-1]:
        return True
    else:
        return False


def sell_or_buy(df, i, status):
    if status == 0 and buy_signal_macd(df, i):
        return 'buy'
    elif status == 1 and sell_signal_macd(df, i):
        return 'sell'
    else:
        return 'hold'
