import numpy as np
import math


def buy_sell(df, sell_or_buy):
    Buy = []
    Sell = []
    status = 0  # status == 1 has positions

    Buy.append(np.nan)
    Sell.append(np.nan)

    for i in range(1, len(df)):
        signal = sell_or_buy(df, i, status)
        if signal == 'buy':
            Buy.append(df['close'][i])
            Sell.append(np.nan)
            status = 1
        elif signal == 'sell':
            Buy.append(np.nan)
            Sell.append(df['close'][i])
            status = 0
        else:
            Buy.append(np.nan)
            Sell.append(np.nan)

    return (Buy, Sell)


def test(init_balance, df, strategy, output='oneline', verbose=False):
    balance = init_balance
    holdings = 0

    a = buy_sell(df, strategy)
    df['Buy_Signal_price'] = a[0]
    df['Sell_Signal_price'] = a[1]

    trade_history = []

    curr_trade = {}

    for i in range(0, len(df)):
        if not math.isnan(df['Buy_Signal_price'][i]):
            purchase = math.floor(balance/df['Buy_Signal_price'][i])
            cost = purchase * df['Buy_Signal_price'][i]

            holdings += purchase
            balance -= cost
            curr_trade['open'] = df['Buy_Signal_price'][i]
            curr_trade['amount'] = purchase
            curr_trade['open_time'] = df['Time'][i]

            if verbose:
                print("{}: Buy {} @ {}, balance = {}".format(
                    df.index[i], purchase, df['Buy_Signal_price'][i], balance))
        elif not math.isnan(df['Sell_Signal_price'][i]) and holdings > 0:
            balance += holdings * df['Sell_Signal_price'][i]
            curr_trade['close'] = df['Sell_Signal_price'][i]
            curr_trade['amount'] = holdings
            curr_trade['close_time'] = df['Time'][i]
            curr_trade['profit'] = (
                curr_trade['close'] - curr_trade['open']) / curr_trade['open']

            trade_history.append(curr_trade)

            curr_trade = {}
            if verbose:
                print("{}: Sell {} @ {}, balance = {}".format(
                    df.index[i], holdings, df['Sell_Signal_price'][i], balance))
            holdings = 0

    num_win = 0
    total_win = 0
    max_win = 0
    num_lose = 0
    total_lose = 0
    max_lose = 0
    total_duration = 0
    max_duration, min_duration = 0, len(df)

    for i in range(0, len(trade_history)):
        curr_trade = trade_history[i]
        if curr_trade['profit'] > 0:
            num_win += 1
            total_win += curr_trade['profit']
            max_win = curr_trade['profit'] if curr_trade['profit'] > max_win else max_win
        else:
            num_lose += 1
            total_lose += curr_trade['profit']
            max_lose = curr_trade['profit'] if curr_trade['profit'] < max_lose else max_lose

        duration = (curr_trade['close_time'] -
                    curr_trade['open_time']).total_seconds() / 3600
        total_duration += duration
        max_duration = duration if duration > max_duration else max_duration
        min_duration = duration if duration < min_duration else min_duration

    final_balance = balance + holdings * df.iloc[-1]['close']
    final_profit = float(final_balance - init_balance) / init_balance * 100
    win_rate = float(num_win / len(trade_history)) * \
        100 if len(trade_history) > 0 else 0.0

    if output == "oneline":
        if len(trade_history) > 0:
            print("Balance: {0:.2f} (Profit:{1:.2f}%, # of Trade:{2}, Win:{3:.2f}%, avg: win {4:.2f}% / lose {5:.2f}%)"
                  .format(final_balance,
                          final_profit,
                          len(trade_history),
                          win_rate,
                          total_win / len(trade_history) * 100,
                          total_lose / len(trade_history) * 100))
        else:
            print("Balance: {0: .2f} (Profit:{1: .2f}%, # of Trade:{2})"
                  .format(final_balance,
                          final_profit,
                          len(trade_history)))

    elif output == "report" and len(trade_history) > 0:
        print("Total # of Trades: {}".format(len(trade_history)))
        print("# Wins: {}".format(num_win))
        print("Max Win: {}%".format(max_win * 100))
        print("Win Rate: {}%".format(win_rate))
        print("# Loses: {}".format(num_lose))
        print("Max Lose: {}%".format(max_lose * 100))
        print("Avg Lose: {}%".format(total_lose / len(trade_history) * 100))
        print("Max Duration: {}".format(max_duration))
        print("Min Duration: {}".format(min_duration))
        print("Avg Duration: {}".format(total_duration / len(trade_history)))

    if verbose:
        for i in range(0, len(trade_history)):
            print(trade_history[i])

    return (final_profit, win_rate)


def buy_n_hold(init_balance, df, output="oneline"):
    purchase = math.floor(init_balance/df['close'][0])
    cost = purchase * df['close'][0]
    last_price = df.iloc[-1]['close']

    final_Profit = float((last_price*purchase - cost)/init_balance*100)

    if output == "oneline":
        print("Asset: {0:.2f} (Profit:{1:.2f}%)".format(
            init_balance - cost + last_price*purchase, final_Profit))

    return final_Profit
