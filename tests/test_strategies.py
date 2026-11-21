import unittest

import numpy as np
import pandas as pd

from strategy.strategy_wma import Strategy_WMA


def make_df(n=600, seed=7):
    # finta's TA wrappers require a full OHLCV frame.
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(0, 1, n))
    return pd.DataFrame({
        "open": close,
        "high": close * 1.01,
        "low": close * 0.99,
        "close": close,
        "volume": np.full(n, 1000.0),
    })


def with_signal(df, last_buy, last_sell):
    df = df.copy()
    df["last_signal"] = [(last_buy, last_sell)] * len(df)
    return df


class TestSellOrBuyHoldLogic(unittest.TestCase):
    def setUp(self):
        self.strategy = Strategy_WMA()

    def test_no_crossover_holds(self):
        for status in (0, 1):
            df = with_signal(make_df(), 0, 0)
            self.assertEqual(self.strategy.sell_or_buy(df, 10, status), "hold")

    def test_nan_signal_holds(self):
        for status in (0, 1):
            df = with_signal(make_df(), np.nan, np.nan)
            self.assertEqual(self.strategy.sell_or_buy(df, 10, status), "hold")

    def test_buy_signal_buys_when_flat(self):
        df = with_signal(make_df(), 10, 0)
        self.assertEqual(self.strategy.sell_or_buy(df, 10, 0), "buy")

    def test_buy_signal_holds_when_holding(self):
        df = with_signal(make_df(), 10, 0)
        self.assertEqual(self.strategy.sell_or_buy(df, 10, 1), "hold")

    def test_sell_signal_sells_when_holding(self):
        df = with_signal(make_df(), 0, 10)
        self.assertEqual(self.strategy.sell_or_buy(df, 10, 1), "sell")

    def test_sell_signal_holds_when_flat(self):
        df = with_signal(make_df(), 0, 10)
        self.assertEqual(self.strategy.sell_or_buy(df, 10, 0), "hold")


class TestPrepData(unittest.TestCase):
    def setUp(self):
        self.strategy = Strategy_WMA()
        self.df = make_df()

    def test_swapped_periods_match(self):
        # Reversed fast/slow args must be swapped, not collapsed to equal periods.
        a = self.strategy.prep_data(self.df, 24, 12)
        b = self.strategy.prep_data(self.df, 12, 24)
        self.assertTrue(np.allclose(a["fast"], b["fast"], equal_nan=True))
        self.assertTrue(np.allclose(a["slow"], b["slow"], equal_nan=True))

    def test_default_periods_are_distinct(self):
        df = self.strategy.prep_data(self.df)
        self.assertFalse(np.allclose(df["fast"][26:], df["slow"][26:]))


if __name__ == "__main__":
    unittest.main()
