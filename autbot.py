import getopt
import time
import os
import logging
import yaml
import json
import math
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from data_preparation import *
from misc import *
from strategy.strategy_wma import Strategy_WMA
from strategy.strategy_macd import Strategy_MACD
from strategy.strategy_supertrend import Strategy_SuperTrend
from strategy.strategy_hma import Strategy_HMA
from strategy.strategy_rvwma import Strategy_RVWMA


def get_strategy(strategy_name):
    if strategy_name == "wma":
        strategy = Strategy_WMA()
    elif strategy_name == "macd":
        strategy = Strategy_MACD()
    elif strategy_name == "supertrend":
        strategy = Strategy_SuperTrend()
    elif strategy_name == "hma":
        strategy = Strategy_HMA()
    elif strategy_name == "rvwma":
        strategy = Strategy_RVWMA()
    else:
        raise Exception("Strategy not found.")

    return strategy


def scan(account_info="accounts.yaml", config="config.yaml"):

    with open(account_info, "r") as file:
        accounts = yaml.load(file, Loader=yaml.FullLoader)

    with open(config, "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    email_sender_username = accounts["gmail_username"]
    email_sender_password = accounts["gmail_password"]

    status_file = config["status_file"]
    history_file = config["history_file"]
    log_file = config["log_file"]
    refresh_interval = config["refresh"]
    data_granularity = config["interval"]
    enable_sound = config["enable_sound"] if "enable_sound" in config else False

    toaddr = config["email_receivers"]
    email_prefix = config["email_prefix"] if "email_prefix" in config else None
    email_mode = config["email_mode"] if "email_mode" in config else "reminder"
    init_balance = config["init_balance"]
    strategy_name = config["strategy"]
    strategy_params = config["strategy_params"]
    ticker_strategy = config["ticker_strategy"] if "ticker_strategy" in config else None
    ticker_list = (
        list(ticker_strategy.keys())
        if ticker_strategy
        else config["watch_list"]
        if "watch_list" in config
        else None
    )
    if not ticker_list or len(ticker_list) == 0:
        raise Exception("Watchlist is empty.")

    Path(os.path.dirname(status_file)).mkdir(parents=True, exist_ok=True)
    Path(os.path.dirname(history_file)).mkdir(parents=True, exist_ok=True)
    Path(os.path.dirname(log_file)).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    strategy = get_strategy(strategy_name)

    if enable_sound:
        from playsound import playsound

    if not os.path.exists(status_file):
        print("Status file does not exist!")
        status_list = {}
    else:
        with open(status_file, "rb") as infile:
            status_list = json.load(infile)

    for ticker in ticker_list:
        if ticker not in status_list:
            status_list[ticker] = {
                "status": 0,
                "balance_cash": init_balance,
                "holding_num": 0,
            }

    while True:
        now = datetime.now()
        print(now)
        if now.weekday() > 4 and now.weekday() < 6:
            break

        if (
            now.hour >= 13 or now.hour < 6
        ):  # for PST, if you are in EST change it to 16 and 9
            next_wake_time = now
            if now.hour > 13:
                next_wake_time += timedelta(days=1)
            next_wake_time = next_wake_time.replace(hour=6, minute=00, second=0)
            delta = next_wake_time - now
            logging.info(f"Go to sleep now, will wake up at {next_wake_time}...")
            if enable_sound:
                playsound("resources/snoring.mp3")
            time.sleep(delta.seconds)
        else:
            t = time.process_time()
            hold_list = []
            trade_list = []
            info_str = ""
            receipt_str = ""

            for i, ticker in enumerate(ticker_list):
                # batch download
                if i % 5 == 0:
                    batch_list = ticker_list[i : i + 5]
                    dfs, _ = mass_refresh(
                        batch_list, period="10d", interval=data_granularity,
                    )
                df = dfs[ticker]
                close_price = df.iloc[-1]["close"]

                if ticker_strategy and ticker_strategy[ticker]:
                    t_strategy = get_strategy(ticker_strategy[ticker][0])
                    df = t_strategy.prep_data(
                        df,
                        float(ticker_strategy[ticker][1]),
                        float(ticker_strategy[ticker][2]),
                    )
                    sign = t_strategy.sell_or_buy(
                        df, len(df) - 1, status_list[ticker]["status"]
                    )
                else:
                    df = strategy.prep_data(
                        df, float(strategy_params[0]), float(strategy_params[1])
                    )
                    sign = strategy.sell_or_buy(
                        df, len(df) - 1, status_list[ticker]["status"]
                    )

                if sign != "hold":
                    trade_list.append(ticker)
                    transaction_num = 0

                    if sign == "buy":
                        transaction_num = math.floor(
                            status_list[ticker]["balance_cash"] * 0.95 / close_price
                        )

                        if transaction_num > 0:
                            status_list[ticker]["holding_num"] += transaction_num
                            status_list[ticker]["balance_cash"] -= (
                                transaction_num * close_price
                            )
                            status_list[ticker]["status"] = 1
                            if enable_sound:
                                playsound("resources/register.mp3")
                        else:
                            logging.warning("Insufficient Budget! - {}".format(cash))

                    elif sign == "sell":
                        transaction_num = status_list[ticker]["holding_num"]

                        status_list[ticker]["balance_cash"] += (
                            transaction_num * close_price
                        )
                        status_list[ticker]["holding_num"] = 0
                        status_list[ticker]["status"] = 0
                        if enable_sound:
                            playsound("resources/coin.mp3")

                    if email_mode == "reminder":
                        transcation_record = (
                            f"{sign.upper()} {ticker} @ {close_price:.2f}"
                        )
                    else:
                        transcation_record = f"{sign.upper()} {transaction_num} {ticker} @ {close_price:.2f}"

                    logging.info(transcation_record)
                    info_str += f"{transcation_record}!\n"

                    update_trade_history(
                        ticker, sign, transaction_num, close_price, history_file
                    )

                else:
                    hold_list.append(ticker)

            with open(status_file, "w", encoding="utf8") as f:
                json.dump(status_list, f, indent=4)

            if len(trade_list) > 0:
                header = (
                    f"[AuTBot][{email_prefix}]"
                    if email_prefix and email_prefix.strip()
                    else "[AuTBot]"
                )
                if len(trade_list) > 1:
                    trade_list_str = "/".join(trade_list)
                    title = (
                        "Trade Reminder"
                        if email_mode == "reminder"
                        else "Trade Notification"
                    )
                    header += f" {title} for {trade_list_str}!"
                else:
                    header += f" {info_str}!"

                send_email(
                    header,
                    info_str,
                    toaddr,
                    email_sender_username,
                    email_sender_password,
                )

            if len(hold_list) > 0:
                if len(hold_list) > 10:
                    hold_list_str = (
                        ", ".join(hold_list[:10])
                        + f" and {len(hold_list)-10} more tickers."
                    )
                else:
                    hold_list_str = ", ".join(hold_list)
                print(f"HOLD: {hold_list_str}")

            elapsed_time = time.process_time() - t
            print("Total Running Time: {:.2f} second.".format(elapsed_time))

            time.sleep(refresh_interval - elapsed_time)


def main(argv):
    current_file = os.path.basename(__file__)
    usage_msg = f"Usage: {current_file} -a <account_info_file> -c <config_file>"

    account_info_file = ""
    config_file = ""

    try:
        opts, args = getopt.getopt(argv, "ha:c:", ["account_info=", "config="])
    except getopt.GetoptError:
        print(f"Option error, please try again.\n{usage_msg}")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(f"Help.\n{usage_msg}")
            sys.exit()
        elif opt in ("-a", "--account_info"):
            account_info_file = arg
        elif opt in ("-c", "--config"):
            config_file = arg

    if account_info_file == "":
        print(f"Account Info is missing, please try again.\n{usage_msg}")
        sys.exit(2)
    if config_file == "":
        print(f"Config file is missing, please try again.\n{usage_msg}")
        sys.exit(2)

    print(f'account_info file is "{account_info_file}"')
    print(f'config_file is "{config_file}"')

    scan(account_info=account_info_file, config=config_file)


if __name__ == "__main__":
    main(sys.argv[1:])
