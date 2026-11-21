import numpy as np
from finta import TA


class Strategy_RVWMA:
    def get_strategy_name(self):
        return "rvwma"

    def rolling_vwma(self, df, rolling_period):
        cv = df["close"] * df["volume"]
        r_cv = cv.rolling(rolling_period).sum()
        r_v = df["volume"].rolling(rolling_period).sum()
        rvwma = (r_cv / r_v).bfill()
        return rvwma

    def prep_data(self, df, rvwma_period=34, wma_period=21):
        rvwma_period = int(rvwma_period)
        wma_period = int(wma_period)

        df = df.copy()

        df["wma"] = TA.WMA(df, wma_period)
        df["rvwma"] = self.rolling_vwma(df, rvwma_period)
        df["last_signal"] = self.calcLastSignal(df, max(wma_period, rvwma_period))
        return df

    def buy_signal_rvwma(self, df, i):
        if i == 0:
            return False
        if df["wma"][i] >= df["rvwma"][i] and df["wma"][i - 1] < df["rvwma"][i - 1]:
            return True
        else:
            return False

    def sell_signal_rvwma(self, df, i):
        if i == 0:
            return False
        if df["wma"][i] <= df["rvwma"][i] and df["wma"][i - 1] > df["rvwma"][i - 1]:
            return True
        else:
            return False

    def calcLastSignal(self, df, initialOffset):
        last_signal = [(np.nan, np.nan)] * len(df)
        last_buy, last_sell = 0, 0

        for i in range(initialOffset + 1, len(df)):
            if self.buy_signal_rvwma(df, i):
                last_buy = i
            elif self.sell_signal_rvwma(df, i):
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
