import numpy as np
from finta import TA


class Strategy_MACD:
    def get_strategy_name(self):
        return "macd"

    def prep_data(self, df, fast_period=12, slow_period=24):
        fast_period = int(fast_period)
        slow_period = int(slow_period)

        if fast_period > slow_period:
            fast_period = slow_period

        shortEMA = df["close"].ewm(span=fast_period, adjust=False).mean()
        longEMA = df["close"].ewm(span=slow_period, adjust=False).mean()

        MACD = shortEMA - longEMA
        signal = MACD.ewm(span=9, adjust=False).mean()
        df["MACD"] = MACD
        df["Signal"] = signal

        df["last_signal"] = self.calcLastSignal(df, slow_period)
        return df

    def buy_signal_macd(self, df, i):
        if i == 0:
            return False
        if df["MACD"][i] >= df["Signal"][i] and df["MACD"][i - 1] < df["Signal"][i - 1]:
            return True
        else:
            return False

    def sell_signal_macd(self, df, i):
        if i == 0:
            return False
        if df["MACD"][i] <= df["Signal"][i] and df["MACD"][i - 1] > df["Signal"][i - 1]:
            return True
        else:
            return False

    def calcLastSignal(self, df, initialOffset):
        last_signal = [(np.nan, np.nan)] * len(df)
        last_buy, last_sell = 0, 0

        for i in range(initialOffset + 1, len(df)):
            if self.buy_signal_macd(df, i):
                last_buy = i
            elif self.sell_signal_macd(df, i):
                last_sell = i

            last_signal[i] = (last_buy, last_sell)

        return last_signal

    def sell_or_buy(self, df, i, status):
        last_sign = (
            "buy" if df["last_signal"][i][0] > df["last_signal"][i][1] else "sell"
        )
        if status == 0 and last_sign == "buy":
            return "buy"
        elif status == 1 and last_sign == "sell":
            return "sell"
        else:
            return "hold"

