import numpy as np
import matplotlib.pyplot as plt
from finta import TA
from backtest import *


def prep_data(df, multiplier=3, atr_period=50):
    df['atr'] = TA.ATR(df, atr_period)
    df['up'] = df['open'] - (multiplier * df['atr'])
    df['up2'] = df['up'].bfill()
    df['dn'] = df['open']+(multiplier*df['atr'])
    df['dn2'] = df['dn'].bfill()
    df['s_up'] = s_up(df)
    df['s_dn'] = s_dn(df)
    df['trend'] = get_trend(df)

    return df


def s_up(df):
    s_up = []
    s_up.append(df['up2'][0])
    for i in range(1, len(df)):
        if df['up2'][i] > s_up[-1] or df['close'][i-1] < s_up[-1]:
            s_up.append(df['up2'][i])
        else:
            s_up.append(s_up[-1])
    return s_up


def s_dn(df):
    s_dn = []
    s_dn.append(df['dn2'][0])
    for i in range(1, len(df)):
        if df['dn2'][i] < s_dn[-1] or df['close'][i-1] > s_dn[-1]:
            s_dn.append(df['dn2'][i])
        else:
            s_dn.append(s_dn[-1])
    return s_dn


def get_trend(df):
    trend = []
    trend.append(1)

    for i in range(1, len(df)):
        curr_trend = trend[-1]
        if trend[-1] == -1 and df['close'][i] > df['s_dn'][i]:
            curr_trend = 1
        elif trend[-1] == 1 and df['close'][i] < df['s_up'][i]:
            curr_trend = -1

        trend.append(curr_trend)

    return trend


def buy_signal_st(df, i):
    if i == 0:
        return False
    if df['trend'][i] == 1 and df['trend'][i-1] == -1:
        return True
    else:
        return False


def sell_signal_st(df, i):
    if i == 0:
        return False
    if df['trend'][i] == -1 and df['trend'][i-1] == 1:
        return True
    else:
        return False


def plot(df, sim=False):
    plt.figure(figsize=(16, 4.5))
    plt.plot(df['s_up'], label='Lowerbound', alpha=0.35)
    plt.plot(df['s_dn'], label='Upperbound', alpha=0.35)
    plt.plot(df['close'], label='close', alpha=0.35)
    if sim:
        buy, sell = buy_sell(df, sell_or_buy)
        plt.scatter(df.index, buy,
                    color='green', label='buy', marker='^', alpha=1)
        plt.scatter(df.index, sell,
                    color='red', label='sell', marker='v', alpha=1)
    plt.title('SuperTrend Strategy')
    plt.xticks(rotation=45)
    plt.ylabel('Price')
    plt.legend(loc='upper left')

    plt.figure(figsize=(16, 2))
    plt.plot(df['trend'], label='trend', color='red')
    #plt.legend(loc='upper left')
    plt.xticks(rotation=45)
    plt.xlabel('Time')
    plt.show()


def sell_or_buy(df, i, status):
    if status == 0 and buy_signal_st(df, i):
        return 'buy'
    elif status == 1 and sell_signal_st(df, i):
        return 'sell'
    else:
        return 'hold'
