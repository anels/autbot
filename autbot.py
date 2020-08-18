import getopt
import time
import os
import logging
import yaml
import json
import math
import sys
import pandas as pd
import robin_stocks as r
from datetime import datetime, timedelta
from playsound import playsound
from data_preparation import *
from misc import *


def format_robinhood_trade_receipt(ticker, r_receipt):
    return "{}: {} {} {} {} @ {} - {}".format(r_receipt["created_at"],
                                              r_receipt["type"],
                                              r_receipt["side"],
                                              r_receipt["quantity"],
                                              ticker,
                                              r_receipt["price"],
                                              r_receipt["state"])


def get_strategy(strategy_name):
    if strategy_name == "kagi":
        from strategy import strategy_kagi as strategy
    elif strategy_name == "wma":
        from strategy import strategy_wma as strategy
    elif strategy_name == "macd":
        from strategy import strategy_macd as strategy
    elif strategy_name == "supertrend":
        from strategy import strategy_supertrend as strategy
    elif strategy_name == "hma":
        from strategy import strategy_hma as strategy
    elif strategy_name == "rvwma":
        from strategy import strategy_rvwma as strategy
    else:
        raise Exception('Strategy not found.')

    return strategy


def scan(account_info='accounts.yaml', config='config_rt_bot.yaml'):

    with open(account_info, 'r') as file:
        accounts = yaml.load(file, Loader=yaml.FullLoader)

    with open(config, 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    robinhood_username = accounts['robinhood_username']
    robinhood_password = accounts['robinhood_password']
    email_sender_username = accounts['gmail_username']
    email_sender_password = accounts['gmail_password']
    status_file = config['status_file']
    history_file = config['history_file']
    log_file = config['log_file']
    refresh_interval = config['refresh']
    toaddr = config['email_receivers']
    email_prefix = config['email_prefix']
    email_mode = config['email_mode']
    init_balance = config['init_balance']
    enable_robinhood = config['enable_robinhood']
    ticker_list = config['watch_list']
    strategy_name = config['strategy']
    strategy_params = config['strategy_params']

    os.makedirs(os.path.dirname(status_file), exist_ok=True)
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(filename=log_file,
                        level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    if enable_robinhood:
        login = r.login(robinhood_username, robinhood_password)
        logging.info("Robinhood Login: {}, the token will be expired in {} seconds.".format(
            login['detail'], login['expires_in']))

    strategy = get_strategy(strategy_name)

    if not os.path.exists(status_file):
        print("Status file does not exist!")

        status_list = {}
        for ticker in ticker_list:
            status_list[ticker] = {'status': 0,
                                   'balance_cash': init_balance, 'holding_num': 0}

        with open(status_file, "w", encoding='utf8') as f:
            json.dump(status_list, f,  indent=6)

    with open(status_file, 'rb') as infile:
        status_list = json.load(infile)

    for ticker in ticker_list:
        if ticker not in status_list:
            status_list[ticker] = {
                'status': 0, 'balance_cash': init_balance, 'holding_num': 0}

    while True:
        now = datetime.now()
        print(now)
        if now.weekday() > 4 and now.weekday() < 6:
            break

        if now.hour >= 13 or now.hour < 6:
            next_wake_time = now + timedelta(days=1)
            next_wake_time = next_wake_time.replace(
                hour=6, minute=00, second=0)
            delta = next_wake_time - now
            logging.info(
                f"Go to sleep now, will wake up at {next_wake_time}...")
            playsound('resources/snoring.mp3')
            time.sleep(delta.seconds)
        else:
            hold_list = []
            trade_list = []
            info_str = ""
            receipt_str = ""

            dfs, _ = mass_refresh(ticker_list, period='5d',
                                  interval=config['interval'])

            for ticker in ticker_list:
                df = dfs[ticker]
                close_price = df.iloc[-1]['close']

                df = strategy.prep_data(
                    df, float(strategy_params[0]), float(strategy_params[1]))
                sign = strategy.sell_or_buy(
                    df, len(df)-1, status_list[ticker]['status'])

                if sign != 'hold':
                    trade_list.append(ticker)
                    transaction_num = 0

                    if sign == 'buy':
                        transaction_num = math.floor(
                            status_list[ticker]['balance_cash'] * 0.95 / close_price)

                        if enable_robinhood:
                            # get user profile
                            account_data = r.load_account_profile()
                            cash = float(account_data.get(
                                'unsettled_funds')) + float(account_data.get('cash'))

                            if cash > transaction_num * close_price:
                                r_receipt = r.order_buy_market(
                                    ticker, transaction_num, extendedHours=True)
                                close_price = float(r_receipt["price"])
                                receipt_ex = format_robinhood_trade_receipt(ticker,
                                                                            r_receipt)
                            else:
                                logging.info(
                                    "Insufficient Cash! - {}".format(cash))
                                return

                        status_list[ticker]['holding_num'] += transaction_num
                        status_list[ticker]['balance_cash'] -= transaction_num * close_price
                        status_list[ticker]['status'] = 1
                        playsound('resources/register.mp3')
                    elif sign == 'sell':
                        transaction_num = status_list[ticker]['holding_num']

                        if enable_robinhood:
                            r_receipt = r.order_sell_market(
                                ticker, transaction_num, extendedHours=True)
                            close_price = float(r_receipt["price"])
                            receipt_ex = format_robinhood_trade_receipt(ticker,
                                                                        r_receipt)

                        status_list[ticker]['balance_cash'] += transaction_num * close_price
                        status_list[ticker]['holding_num'] = 0
                        status_list[ticker]['status'] = 0
                        playsound('resources/coin.mp3')

                    if email_mode == "reminder":
                        transcation_record = "{} {} @ {:.2f}".format(
                            sign.upper(), ticker, close_price)
                    else:
                        transcation_record = "{} {} {} @ {:.2f}".format(
                            sign.upper(), transaction_num, ticker, close_price)

                    logging.info(transcation_record)
                    info_str += "{}!\n".format(transcation_record)

                    if enable_robinhood:
                        receipt_str += f"{receipt_ex}\n"
                        logging.info(f"Robinhood Receipt: {receipt_ex}")

                    update_trade_history(
                        ticker, sign, transaction_num, close_price, history_file)

                else:
                    hold_list.append(ticker)

            with open(status_file, "w", encoding='utf8') as f:
                json.dump(status_list, f, indent=6)

            if len(trade_list) > 0:
                header = f"[TBot][{email_prefix}]" if email_prefix and email_prefix.strip(
                ) else "[TBot]"
                if len(trade_list) > 1:
                    trade_list_str = "/".join(trade_list)
                    title = " Trade Reminder" if email_mode == "reminder" else " Trade Notification"
                    header += f"{title} for {trade_list_str}!"
                else:
                    headder += f"{info_str}!"

                body_text = info_str
                if enable_robinhood:
                    body_text += f"\n\nRobinhood Receipt:\n{receipt_str }"

                send_email(header,
                           body_text, toaddr, email_sender_username, email_sender_password)

            if len(hold_list) > 0:
                hold_list_str = ", ".join(hold_list)
                print("HOLD: {}".format(hold_list_str))

            time.sleep(refresh_interval)


def main(argv):
    current_file = os.path.basename(__file__)
    usage_msg = f"Usage: {current_file} -a <account_info_file> -c <config_file>"

    account_info_file = ''
    config_file = ''
    try:
        opts, args = getopt.getopt(argv, "ha:c:", ["account_info=", "config="])
    except getopt.GetoptError:
        print("Option error, please try again.\n{}".format(usage_msg))
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("Help.\n{}".format(usage_msg))
            sys.exit()
        elif opt in ("-a", "--account_info"):
            account_info_file = arg
        elif opt in ("-c", "--config"):
            config_file = arg

    if account_info_file == "":
        print("Account Info is missing, please try again.\n{}".format(usage_msg))
        sys.exit(2)
    if config_file == "":
        print("Config file is missing, please try again.\n{}".format(usage_msg))
        sys.exit(2)

    print('account_info file is \"{}\"'.format(account_info_file))
    print('config_file is \"{}\"'.format(config_file))

    scan(account_info=account_info_file, config=config_file)


if __name__ == "__main__":
    main(sys.argv[1:])
