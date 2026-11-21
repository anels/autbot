import numpy as np
from finta import TA


class Strategy_WMA:
    def get_strategy_name(self):
        return "wma"

    def prep_data(self, df, fast_period=13, slow_period=13):
        fast_period = int(fast_period)
        slow_period = int(slow_period)

        if fast_period > slow_period:
            # Swap instead of collapsing to equal periods (a dead strategy).
            fast_period, slow_period = slow_period, fast_period

        df = df.copy()
        df.loc[:, "fast"] = TA.WMA(df, fast_period, "close")
        df.loc[:, "slow"] = TA.WMA(df, slow_period, "close")
        df["last_signal"] = self.calcLastSignal(df, max(fast_period, slow_period))
        return df

    def buy_signal_wma(self, df, i):
        if i == 0:
            return False
        if df["fast"][i] >= df["slow"][i] and df["fast"][i - 1] > df["slow"][i - 1]:
            return True
        else:
            return False

    def sell_signal_wma(self, df, i):
        if i == 0:
            return False
        if df["fast"][i] < df["slow"][i] and df["fast"][i - 1] >= df["slow"][i - 1]:
            return True
        else:
            return False

    def calcLastSignal(self, df, initialOffset):
        last_signal = [(np.nan, np.nan)] * len(df)
        last_buy, last_sell = 0, 0

        for i in range(initialOffset + 1, len(df)):
            if self.buy_signal_wma(df, i):
                last_buy = i
            elif self.sell_signal_wma(df, i):
                last_sell = i

            last_signal[i] = (last_buy, last_sell)

        return last_signal

    def sell_or_buy(self, df, i, status):
        last_buy, last_sell = df["last_signal"][i]
        if not (last_buy > 0 or last_sell > 0):
            # No crossover observed yet (zeros or NaN): stay flat instead of
            # defaulting to a sell signal.
            return "hold"
        last_sign = "buy" if last_buy > last_sell else "sell"
        if status == 0 and last_sign == "buy":
            return "buy"
        elif status == 1 and last_sign == "sell":
            return "sell"
        else:
            return "hold"
