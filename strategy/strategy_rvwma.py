import numpy as np
import matplotlib.pyplot as plt
from finta import TA
from backtest import *


def rolling_vwma(df, rolling_period):
    cv = df['close'] * df['volume']
    r_cv = cv.rolling(rolling_period).sum()
    r_v = df['volume'].rolling(rolling_period).sum()
    rvwma = (r_cv/r_v).bfill()
    return rvwma


def prep_data(df, rvwma_period=34, wma_period=21):
    df['rvwma'] = rolling_vwma(df, rvwma_period)
    df['wma'] = TA.WMA(df, wma_period)
    return df


def buy_signal_rvwma(df, i):
    if i == 0:
        return False
    if df['wma'][i] >= df['rvwma'][i] and df['wma'][i-1] < df['rvwma'][i-1]:
        return True
    else:
        return False


def sell_signal_rvwma(df, i):
    if i == 0:
        return False
    if df['wma'][i] <= df['rvwma'][i] and df['wma'][i-1] > df['rvwma'][i-1]:
        return True
    else:
        return False


def sell_or_buy(df, i, status):
    if status == 0 and buy_signal_rvwma(df, i):
        return 'buy'
    elif status == 1 and sell_signal_rvwma(df, i):
        return 'sell'
    else:
        return 'hold'


def plot(df, sim=False):
    plt.figure(figsize=(16, 4.5))
    plt.plot(df['rvwma'], label='rvwma', alpha=0.35)
    plt.plot(df['wma'], label='wma', alpha=0.35)
    plt.plot(df['close'], label='close', alpha=0.35)
    if sim:
        buy, sell = buy_sell(df, sell_or_buy)
        plt.scatter(df.index, buy,
                    color='green', label='buy', marker='^', alpha=1)
        plt.scatter(df.index, sell,
                    color='red', label='sell', marker='v', alpha=1)
    plt.title('RVWMA Strategy')
    plt.xlabel('Time')
    plt.xticks(rotation=45)
    plt.ylabel('Price')
    plt.legend(loc='upper left')
