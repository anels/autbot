import numpy as np
from finta import TA


def rolling_vwma(df, rolling_period):
    cv = df['close'] * df['volume']
    r_cv = cv.rolling(rolling_period).sum()
    r_v = df['volume'].rolling(rolling_period).sum()
    rvwma = (r_cv/r_v).bfill()
    return rvwma


def prep_data(df, rvwma_period=34, wma_period=21):
    rvwma_period = int(rvwma_period)
    wma_period = int(wma_period)

    df = df.copy()

    df['wma'] = TA.WMA(df, wma_period)
    df['rvwma'] = rolling_vwma(df, rvwma_period)
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
