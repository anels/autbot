import numpy as np
from finta import TA


class Strategy_SuperTrend:
    def get_strategy_name(self):
        return "supertrend"

    def prep_data(self, df, multiplier=3, atr_period=50):
        multiplier = float(multiplier)
        atr_period = int(atr_period)

        df = df.copy()
        df["atr"] = TA.ATR(df, atr_period)
        df["up"] = df["open"] - (multiplier * df["atr"])
        df["up2"] = df["up"].bfill()
        df["dn"] = df["open"] + (multiplier * df["atr"])
        df["dn2"] = df["dn"].bfill()
        df["s_up"] = self.s_up(df)
        df["s_dn"] = self.s_dn(df)
        df["trend"] = self.get_trend(df)

        df["last_signal"] = self.calcLastSignal(df, atr_period)

        return df

    def s_up(self, df):
        s_up = []
        s_up.append(df["up2"][0])
        for i in range(1, len(df)):
            if df["up2"][i] > s_up[-1] or df["close"][i - 1] < s_up[-1]:
                s_up.append(df["up2"][i])
            else:
                s_up.append(s_up[-1])
        return s_up

    def s_dn(self, df):
        s_dn = []
        s_dn.append(df["dn2"][0])
        for i in range(1, len(df)):
            if df["dn2"][i] < s_dn[-1] or df["close"][i - 1] > s_dn[-1]:
                s_dn.append(df["dn2"][i])
            else:
                s_dn.append(s_dn[-1])
        return s_dn

    def get_trend(self, df):
        trend = []
        trend.append(1)

        for i in range(1, len(df)):
            curr_trend = trend[-1]
            if trend[-1] == -1 and df["close"][i] > df["s_dn"][i]:
                curr_trend = 1
            elif trend[-1] == 1 and df["close"][i] < df["s_up"][i]:
                curr_trend = -1

            trend.append(curr_trend)

        return trend

    def buy_signal_st(self, df, i):
        if i == 0:
            return False
        if df["trend"][i] == 1 and df["trend"][i - 1] == -1:
            return True
        else:
            return False

    def sell_signal_st(self, df, i):
        if i == 0:
            return False
        if df["trend"][i] == -1 and df["trend"][i - 1] == 1:
            return True
        else:
            return False

    def calcLastSignal(self, df, initialOffset):
        last_signal = [(np.nan, np.nan)] * len(df)
        last_buy, last_sell = 0, 0

        for i in range(initialOffset + 1, len(df)):
            if self.buy_signal_st(df, i):
                last_buy = i
            elif self.sell_signal_st(df, i):
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
