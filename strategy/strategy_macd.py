import numpy as np
import matplotlib.pyplot as plt
from finta import TA
from backtest import *


def prep_data(df, fast_period=12, slow_period=24):
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


def plot(df, sim=False):
    f, axarr = plt.subplots(2, sharex=True, figsize=(16, 10))
    f.subplots_adjust(hspace=0)
    axarr[0].plot(df['close'], alpha=0.35)
    if sim:
        buy, sell = buy_sell(df, sell_or_buy)
        axarr[0].scatter(df.index, buy,
                         color='green', label='buy', marker='^', alpha=1)
        axarr[0].scatter(df.index, sell,
                         color='red', label='sell', marker='v', alpha=1)

    axarr[1].plot(df.index, df['MACD'], label='MACD', color='red')
    axarr[1].plot(df.index, df['Signal'], label='Signal',
                  color='blue', alpha=0.35)

    plt.title('MACD Strategy')
