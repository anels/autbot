import numpy as np
from finta import TA
from backtest import *
import matplotlib.pyplot as plt


def prep_data(df, reversal=0.02, period=13):
    reversal = float(reversal)
    period = int(period)
    df['kagi'] = getKagi(df['close'], reversal)
    df['wma'] = TA.WMA(df, period, 'close')
    return df


def getKagi(df, reversal):
    kagi = np.zeros(len(df))

    look_back = 0
    direction = 0  # 0: down, 1: up
    curr_val = df.iloc[0]

    for i in range(0, len(df)):
        if direction == 0:
            if df[i] < curr_val * (1 + reversal):
                curr_val = df[i] if df[i] < curr_val else curr_val
                look_back += 1
            else:
                for j in range(0, look_back):
                    kagi[i-j-1] = curr_val

                curr_val = df[i]
                direction = 1
                look_back = 1
        else:
            if df[i] > curr_val * (1 - reversal):
                curr_val = df[i] if df[i] > curr_val else curr_val
                look_back += 1
            else:
                for j in range(0, look_back):
                    kagi[i-j-1] = curr_val

                curr_val = df[i]
                direction = 0
                look_back = 1

    for j in range(0, look_back):
        kagi[len(df)-j-1] = curr_val

    return kagi


def buy_signal_kagi(df, i):
    if i == 0:
        return False
    if df['wma'][i] <= df['kagi'][i] and df['wma'][i-1] > df['kagi'][i-1]:
        return True
    else:
        return False


def sell_signal_kagi(df, i):
    if i == 0:
        return False
    if df['wma'][i] >= df['kagi'][i] and df['wma'][i-1] < df['kagi'][i-1]:
        return True
    else:
        return False


def sell_or_buy(df, i, status):
    if status == 0:
        if buy_signal_kagi(df, i) or (buy_signal_kagi(df, i-1) and df['wma'][i] <= df['kagi'][i]):
            return 'buy'
        else:
            return 'hold'
    elif status == 1:
        if sell_signal_kagi(df, i) or (sell_signal_kagi(df, i-1) and df['wma'][i] >= df['kagi'][i]):
            return 'sell'
        else:
            return 'hold'
    else:
        return 'hold'


def plot(df, sim=False):
    plt.figure(figsize=(16, 4.5))
    plt.plot(df['kagi'], label='kagi', alpha=0.35)
    plt.plot(df['wma'], label='wma', alpha=0.35)
    plt.plot(df['close'], label='close', alpha=0.35)
    if sim:
        buy, sell = buy_sell(df, sell_or_buy)
        plt.scatter(df.index, buy,
                    color='green', label='buy', marker='^', alpha=1)
        plt.scatter(df.index, sell,
                    color='red', label='sell', marker='v', alpha=1)
    plt.title('KAGI Strategy')
    plt.xlabel('Time')
    plt.xticks(rotation=45)
    plt.ylabel('Price')
    plt.legend(loc='upper left')
