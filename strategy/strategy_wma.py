import numpy as np
from finta import TA
import matplotlib.pyplot as plt
from backtest import *


def prep_data(df, wma_period=13, ema_period=13):
    wma_period = int(wma_period)
    ema_period = int(ema_period)
    df['wma'] = TA.WMA(df, wma_period, 'close')
    df['ema'] = TA.EMA(df, ema_period, 'close')
    return df


def buy_signal_wma(df, i):
    if i == 0:
        return False
    if df['wma'][i] >= df['ema'][i] and df['wma'][i-1] > df['ema'][i-1]:
        return True
    else:
        return False


def sell_signal_wma(df, i):
    if i == 0:
        return False
    if df['wma'][i] < df['ema'][i] and df['wma'][i-1] >= df['ema'][i-1]:
        return True
    else:
        return False


def sell_or_buy(df, i, status):
    if status == 0 and buy_signal_wma(df, i):
        return 'buy'
    elif status == 1 and sell_signal_wma(df, i):
        return 'sell'
    else:
        return 'hold'


def plot(df, sim=False):
    plt.figure(figsize=(16, 4.5))
    plt.plot(df['wma'], label='wma', alpha=0.35)
    plt.plot(df['ema'], label='ema', alpha=0.35)
    plt.plot(df['close'], label='close', alpha=0.35)
    if sim:
        buy, sell = buy_sell(df, sell_or_buy)
        plt.scatter(df.index, buy,
                    color='green', label='buy', marker='^', alpha=1)
        plt.scatter(df.index, sell,
                    color='red', label='sell', marker='v', alpha=1)
    plt.title('WMA Strategy')
    plt.xlabel('Time')
    plt.xticks(rotation=45)
    plt.ylabel('Price')
    plt.legend(loc='upper left')
