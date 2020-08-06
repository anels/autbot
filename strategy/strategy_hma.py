import numpy as np
import matplotlib.pyplot as plt
from finta import TA
from backtest import *


def prep_data(df, fast_period=12, slow_period=24):
    df['hma_fast'] = TA.HMA(df, fast_period)
    df['hma_slow'] = TA.HMA(df, slow_period)
    return df


def buy_signal_hma(df, i):
    if i == 0:
        return False
    if df['hma_fast'][i] >= df['hma_slow'][i] and df['hma_fast'][i-1] < df['hma_slow'][i-1]:
        return True
    else:
        return False


def sell_signal_hma(df, i):
    if i == 0:
        return False
    if df['hma_fast'][i] <= df['hma_slow'][i] and df['hma_fast'][i-1] > df['hma_slow'][i-1]:
        return True
    else:
        return False


def sell_or_buy(df, i, status):
    if status == 0 and buy_signal_hma(df, i):
        return 'buy'
    elif status == 1 and sell_signal_hma(df, i):
        return 'sell'
    else:
        return 'hold'


def plot(df, sim=False):
    plt.figure(figsize=(16, 4.5))
    plt.plot(df['hma_fast'], label='hma_fast', alpha=0.35)
    plt.plot(df['hma_slow'], label='hma_slow', alpha=0.35)
    plt.plot(df['close'], label='close', alpha=0.35)
    if sim:
        buy, sell = buy_sell(df, sell_or_buy)
        plt.scatter(df.index, buy,
                    color='green', label='buy', marker='^', alpha=1)
        plt.scatter(df.index, sell,
                    color='red', label='sell', marker='v', alpha=1)
    plt.title('HMA Strategy')
    plt.xlabel('Time')
    plt.xticks(rotation=45)
    plt.ylabel('Price')
    plt.legend(loc='upper left')
