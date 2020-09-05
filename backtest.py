import matplotlib.pyplot as plt
import numpy as np
import math
from data_preparation import *
from misc import timeit


def buy_sell(df, sell_or_buy, start=500):
    Buy = []
    Sell = []
    status = 0  # status == 1 has positions

    for i in range(start):
        Buy.append(np.nan)
        Sell.append(np.nan)

    for i in range(start, len(df)):
        signal = sell_or_buy(df, i, status)
        if signal == "buy":
            Buy.append(df["close"][i])
            Sell.append(np.nan)
            status = 1
        elif signal == "sell":
            Buy.append(np.nan)
            Sell.append(df["close"][i])
            status = 0
        else:
            Buy.append(np.nan)
            Sell.append(np.nan)

    return (Buy, Sell)


def test(init_balance, df, strategy, output="oneline", verbose=False):
    balance = init_balance
    holdings = 0

        a = buy_sell(df, strategy)
    df["Buy_Signal_price"] = a[0]
    df["Sell_Signal_price"] = a[1]

    trade_history = []
    curr_trade = {}

    for i in range(0, len(df)):
        if not math.isnan(df["Buy_Signal_price"][i]):
            purchase = math.floor(balance / df["Buy_Signal_price"][i])
            cost = purchase * df["Buy_Signal_price"][i]

            holdings += purchase
            balance -= cost
            curr_trade["open"] = df["Buy_Signal_price"][i]
            curr_trade["amount"] = purchase
            curr_trade["open_time"] = df["Time"][i]

            if verbose:
                print(
                    "{}: Buy {} @ {}, balance = {}".format(
                        df["Time"][i], purchase, df["Buy_Signal_price"][i], balance
                    )
                )
        elif not math.isnan(df["Sell_Signal_price"][i]) and holdings > 0:
            balance += holdings * df["Sell_Signal_price"][i]
            curr_trade["close"] = df["Sell_Signal_price"][i]
            curr_trade["amount"] = holdings
            curr_trade["close_time"] = df["Time"][i]
            curr_trade["profit"] = (
                curr_trade["close"] - curr_trade["open"]
            ) / curr_trade["open"]

            trade_history.append(curr_trade)

            curr_trade = {}
            if verbose:
                print(
                    "{}: Sell {} @ {}, balance = {}".format(
                        df["Time"][i], holdings, df["Sell_Signal_price"][i], balance
                    )
                )
            holdings = 0

    num_trade = len(trade_history)

    num_win = 0
    total_win = 0
    max_win = 0
    num_lose = 0
    total_lose = 0
    max_lose = 0
    total_duration = 0
    max_duration, min_duration = 0, len(df)

    for i in range(num_trade):
        curr_trade = trade_history[i]
        if curr_trade["profit"] > 0:
            num_win += 1
            total_win += curr_trade["profit"]
            max_win = (
                curr_trade["profit"] if curr_trade["profit"] > max_win else max_win
            )
        else:
            num_lose += 1
            total_lose += curr_trade["profit"]
            max_lose = (
                curr_trade["profit"] if curr_trade["profit"] < max_lose else max_lose
            )

        duration = (
            curr_trade["close_time"] - curr_trade["open_time"]
        ).total_seconds() / 3600
        total_duration += duration
        max_duration = duration if duration > max_duration else max_duration
        min_duration = duration if duration < min_duration else min_duration

    final_balance = balance + holdings * df.iloc[-1]["close"]
    final_profit = float(final_balance - init_balance) / init_balance * 100
    win_rate = float(num_win / num_trade) * 100 if num_trade > 0 else 0.0

    if output == "oneline":
        if num_trade > 0:
            print(
                "Balance: {0:.2f} (Profit:{1:.2f}%, # of Trade:{2}, Win:{3:.2f}%, avg: win {4:.2f}% / lose {5:.2f}%)".format(
                    final_balance,
                    final_profit,
                    num_trade,
                    win_rate,
                    total_win / num_trade * 100,
                    total_lose / num_trade * 100,
                )
            )
        else:
            print(
                "Balance: {0: .2f} (Profit:{1: .2f}%, # of Trade:{2})".format(
                    final_balance, final_profit, num_trade
                )
            )

    elif output == "report" and num_trade > 0:
        print("Total # of Trades: {}".format(num_trade))
        print("# Wins: {}".format(num_win))
        print("Max Win: {}%".format(max_win * 100))
        print("Win Rate: {}%".format(win_rate))
        print("# Loses: {}".format(num_lose))
        print("Max Lose: {}%".format(max_lose * 100))
        print("Avg Lose: {}%".format(total_lose / num_trade * 100))
        print("Max Duration: {}".format(max_duration))
        print("Min Duration: {}".format(min_duration))
        print("Avg Duration: {}".format(total_duration / num_trade))

    # if verbose:
    #    for i in range(0, len(trade_history)):
    #        print(trade_history[i])

    return (final_profit, win_rate, num_trade)


def buy_n_hold(init_balance, df, start=500, output="oneline"):
    purchase = math.floor(init_balance / df["close"][start])
    cost = purchase * df["close"][start]
    last_price = df.iloc[-1]["close"]

    final_Profit = float((last_price * purchase - cost) / init_balance * 100)

    if output == "oneline":
        print(
            "Asset: {0:.2f} (Profit:{1:.2f}%)".format(
                init_balance - cost + last_price * purchase, final_Profit
            )
        )

    return final_Profit


def plot_heatmap(test_result, title, x_label, y_label):
    fig, ax = plt.subplots(figsize=(9, 9))
    im = ax.imshow(test_result, cmap="RdYlGn")

    # We want to show all ticks...
    ax.set_yticks(np.arange(len(x_label)))
    ax.set_xticks(np.arange(len(y_label)))
    # ... and label them with the respective list entries
    ax.set_yticklabels(x_label)
    ax.set_xticklabels(y_label)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(x_label)):
        for j in range(len(y_label)):
            text = ax.text(
                j,
                i,
                "{0:.2f}%".format(test_result[i][j]),
                ha="center",
                va="center",
                color="w",
            )

    ax.set_title(title)
    fig.tight_layout()
    plt.show()


# @timeit
def run_benchmark(
    tickers, param_a, param_b, period, interval, strategy, init_balance=10000
):

    profit_results = []
    winrate_results = []
    beat_results = []
    tardenum_results = []
    print("Running Benchmark for {}...".format(strategy.get_strategy_name()))
    for idx, ticker in enumerate(tickers):
        print(
            f">> Testing {ticker: <8} ... {(idx)/len(tickers)*100.0:6.2f}% ({idx}/{len(tickers)})",
            end="\r",
        )
        df, last_update = refresh(ticker, period, interval)
        bnh = buy_n_hold(init_balance, df, output="None")

        p_result = []
        w_result = []
        b_result = []
        t_result = []

        for i in param_a:
            p_result_i = []
            w_result_i = []
            b_result_i = []
            t_result_i = []
            for j in param_b:
                df_test = strategy.prep_data(df, i, j)
                # print ("{},{} => ".format(i, j), end='')
                test_result = test(
                    init_balance, df_test, strategy.sell_or_buy, output="None"
                )
                p_result_i.append(test_result[0] - bnh)
                w_result_i.append(test_result[1])
                b_result_i.append(1 if test_result[0] - bnh > 0 else 0)
                t_result_i.append(test_result[2])
            p_result.append(p_result_i)
            w_result.append(w_result_i)
            b_result.append(b_result_i)
            t_result.append(t_result_i)
        profit_results.append(p_result)
        winrate_results.append(w_result)
        beat_results.append(b_result)
        tardenum_results.append(t_result)

        print(
            " " * 80, end="\r",
        )

    return (profit_results, winrate_results, beat_results, tardenum_results)


def run_strategy(tickers, param_a, param_b, period, interval, strategy, plot_fig=False):
    (p_results, w_results, b_results, t_results) = run_benchmark(
        tickers, param_a, param_b, period, interval, strategy
    )

    total_p = np.zeros_like(p_results[0])  # total profit
    total_b = np.zeros_like(b_results[0])  # total beat (bnh)
    total_w = np.zeros_like(w_results[0])  # total win rates of trades
    total_t = np.zeros_like(t_results[0])  # total number of transactions
    for i in range(len(tickers)):
        total_p = np.add(p_results[i], total_p)
        total_b = np.add(b_results[i], total_b)
        total_w = np.add(w_results[i], total_w)
        total_t = np.add(t_results[i], total_t)
    avg_b = total_b * 100.0 / len(tickers)
    avg_w = total_w / len(tickers)
    avg_t = total_t / len(tickers)

    win_coordinates = np.where(
        total_b > 0.60
    )  # for multiple tickers, make sure at least 60% are beat buy and hold

    res = []

    if len(win_coordinates[0]) == 0:
        max_result = np.max(total_p)
        max_idxes = np.unravel_index(np.argmax(total_p, axis=None), total_p.shape)
        # print(
        #    "The best config for {} is ({}, {}) profit margin is {}%.".format(
        #        strategy.__name__,
        #        param_a[max_idxes[0]],
        #        param_b[max_idxes[1]],
        #        max_result,
        #    )
        # )
    else:
        win_idxes = list(zip(win_coordinates[0], win_coordinates[1]))
        win_picks = []
        for w in win_idxes:
            win_picks.append([w[0], w[1], total_p[w[0]][w[1]], avg_t[w[0]][w[1]]])

        # win_picks = [pick for pick in win_picks if pick[2] > 1.0]
        win_picks.sort(reverse=True, key=lambda i: i[2])

        num_res = min(len(win_picks), 16)

        # print(f"  Find {num_res} winning params.")

        for i in range(num_res):
            # print(
            #     "  The #{} config is ({}, {}, {}) profit margin is {:.4f}%. # of Trade is {}".format(
            #         i + 1,
            #         strategy.get_strategy_name(),
            #         param_a[win_picks[i][0]],
            #         param_b[win_picks[i][1]],
            #         win_picks[i][2],
            #         win_picks[i][3],
            #     )
            # )
            res.append(
                [
                    [
                        strategy.get_strategy_name(),
                        param_a[win_picks[i][0]],
                        param_b[win_picks[i][1]],
                    ],
                    win_picks[i][2],
                    win_picks[i][3],
                ]
            )

    if plot_fig:
        plot_heatmap(
            total_p, f"Profit of {strategy.get_strategy_name()}", param_a, param_b
        )
        # plot_heatmap(avg_b, f"Beat % of {strategy.get_strategy_name()}", param_a, param_b)
        plot_heatmap(
            avg_w, f"Win % of {strategy.get_strategy_name()}", param_a, param_b
        )

    return res


def add_buy_sell_signals(plt, df, signals):
    buy, sell = signals
    plt.scatter(df.index, buy, color="green", label="buy", marker="^", alpha=1)
    plt.scatter(df.index, sell, color="red", label="sell", marker="v", alpha=1)


def plot_wma(df, signals=None, start=500):
    plt.figure(figsize=(16, 4.5))
    plt.plot(df["close"], label="close", alpha=0.35)
    plt.vlines(
        x=start,
        ymin=min(df["close"]),
        ymax=max(df["close"]),
        linestyle="--",
        alpha=0.35,
        color="blue",
    )
    plt.plot(df["wma"], label="wma", alpha=0.35)
    plt.plot(df["ema"], label="ema", alpha=0.35)
    if signals is not None:
        add_buy_sell_signals(plt, df, signals)

    # plt.title('WMA Strategy')
    plt.xlabel("Time")
    plt.xticks(rotation=45)
    plt.ylabel("Price")
    plt.legend(loc="upper left")


def plot_supertrend(df, signals=None, start=500):
    f, axarr = plt.subplots(
        2, sharex=True, figsize=(16, 10), gridspec_kw={"height_ratios": [3, 1]}
    )
    f.subplots_adjust(hspace=0)
    # plt.suptitle('SuperTrend Strategy')
    axarr[0].plot(df["close"], label="close", alpha=0.35)
    axarr[0].vlines(
        x=start,
        ymin=min(df["close"]),
        ymax=max(df["close"]),
        linestyle="--",
        alpha=0.35,
        color="blue",
    )

    axarr[0].plot(df["s_up"], label="Lowerbound", alpha=0.35)
    axarr[0].plot(df["s_dn"], label="Upperbound", alpha=0.35)
    if signals is not None:
        add_buy_sell_signals(axarr[0], df, signals)

    # plt.xticks(rotation=45)
    # plt.ylabel('Price')
    axarr[0].legend(loc="upper left")

    axarr[1].plot(df["trend"], label="trend", color="red")
    axarr[1].legend(loc="upper left")
    # plt.xticks(rotation=45)
    # plt.xlabel('Time')


def plot_rvwma(df, signals=None, start=500):
    plt.figure(figsize=(16, 4.5))
    plt.plot(df["rvwma"], label="rvwma", alpha=0.35)
    plt.plot(df["wma"], label="wma", alpha=0.35)
    plt.plot(df["close"], label="close", alpha=0.35)
    plt.vlines(
        x=start,
        ymin=min(df["close"]),
        ymax=max(df["close"]),
        linestyle="--",
        alpha=0.35,
        color="blue",
    )

    if signals is not None:
        add_buy_sell_signals(plt, df, signals)

    plt.title("RVWMA Strategy")
    plt.xlabel("Time")
    plt.xticks(rotation=45)
    plt.ylabel("Price")
    plt.legend(loc="upper left")


def plot_macd(df, signals=None, start=500):
    f, axarr = plt.subplots(
        2, sharex=True, figsize=(16, 10), gridspec_kw={"height_ratios": [3, 1]}
    )
    f.subplots_adjust(hspace=0)
    axarr[0].plot(df["close"], alpha=0.35)
    axarr[0].vlines(
        x=start,
        ymin=min(df["close"]),
        ymax=max(df["close"]),
        linestyle="--",
        alpha=0.35,
        color="blue",
    )
    if signals is not None:
        add_buy_sell_signals(axarr[0], df, signals)

    # axarr[1].plot(TA.KST(df), alpha=0.5)
    axarr[1].plot(df.index, df["MACD"], label="MACD", color="red")
    axarr[1].plot(df.index, df["Signal"], label="Signal", color="blue", alpha=0.35)

    # plt.title('MACD Strategy')
    # axarr[0].ylabel('Price')
    # axarr[0].legend(loc='upper left')
    # f.xticks(rotation=45)
    # f.xlabel('Time')


def plot_hma(df, signals=None, start=500):
    plt.figure(figsize=(16, 4.5))
    plt.plot(df["hma_fast"], label="hma_fast", alpha=0.35)
    plt.plot(df["hma_slow"], label="hma_slow", alpha=0.35)
    plt.plot(df["close"], label="close", alpha=0.35)
    plt.vlines(
        x=start,
        ymin=min(df["close"]),
        ymax=max(df["close"]),
        linestyle="--",
        alpha=0.35,
        color="blue",
    )
    if signals is not None:
        add_buy_sell_signals(plt, df, signals)

    plt.title("HMA Strategy")
    plt.xlabel("Time")
    plt.xticks(rotation=45)
    plt.ylabel("Price")
    plt.legend(loc="upper left")


def plot_kagi(df, signals=None, start=500):
    plt.figure(figsize=(16, 4.5))
    plt.plot(df["kagi"], label="kagi", alpha=0.35)
    plt.plot(df["wma"], label="wma", alpha=0.35)
    plt.plot(df["close"], label="close", alpha=0.35)
    plt.vlines(
        x=start,
        ymin=min(df["close"]),
        ymax=max(df["close"]),
        linestyle="--",
        alpha=0.35,
        color="blue",
    )
    if signals is not None:
        add_buy_sell_signals(plt, df, signals)

    # plt.title('KAGI Strategy')
    plt.xlabel("Time")
    plt.xticks(rotation=45)
    plt.ylabel("Price")
    plt.legend(loc="upper left")

