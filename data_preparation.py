import yfinance as yf


def refresh(ticker, period="30d", interval="15m"):
    df = yf.Ticker(ticker).history(period=period,  interval=interval)

    df = df.dropna(subset=['High', 'Low', 'Open', 'Close', 'Volume'])
    if df.iloc[-1]['Volume'] == 0:
        df.drop(df.tail(1).index, inplace=True)

    df['Time'] = df.index
    df.index = range(0, len(df))

    df.rename(columns={'High': 'high',
                       'Low': 'low',
                       'Open': 'open',
                       'Close': 'close',
                       'Volume': 'volume'},
              inplace=True)

    last_update = df.iloc[-1]['Time']

    return (df, last_update)
