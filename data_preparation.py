import yfinance as yf


def refresh(ticker, period="30d", interval="15m"):
    df = yf.Ticker(ticker).history(period=period,  interval=interval)

    df['Time'] = df.index

    df = df.dropna(subset=['High', 'Low', 'Open', 'Close', 'Volume'])
    if df.iloc[-1]['Volume'] == 0:
        df.drop(df.tail(1).index, inplace=True)

    df.index = range(0, len(df))

    df.rename(columns={'High': 'high',
                       'Low': 'low',
                       'Open': 'open',
                       'Close': 'close',
                       'Volume': 'volume'},
              inplace=True)

    last_update = df.iloc[-1]['Time']

    return (df, last_update)


def mass_refresh(tickers, period="30d", interval="15m"):
    dfs = yf.download(tickers, group_by='ticker',
                      period=period, interval=interval, progress=False)
    df_dicts = {}

    for ticker in tickers:
        df = dfs[ticker][['High', 'Low', 'Open', 'Close', 'Volume']]

        df['Time'] = df.index
        df = df.dropna(subset=['High', 'Low', 'Open', 'Close', 'Volume'])

        df.index = range(0, len(df))

        df.rename(columns={'High': 'high',
                           'Low': 'low',
                           'Open': 'open',
                           'Close': 'close',
                           'Volume': 'volume'},
                  inplace=True)
        df_dicts[ticker] = df

    last_update = df.iloc[-1]['Time']

    return (df_dicts, last_update)

