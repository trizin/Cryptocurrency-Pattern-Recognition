# %%
import time
from binance.client import Client
from pandas.core.frame import DataFrame
import numpy as np
import pandas as pd
client = Client("", "")
# %%


def binanceDataFrame(klines):
    df = pd.DataFrame(klines.reshape(-1, 12), dtype=float, columns=('Open Time',
                                                                    'Open',
                                                                    'High',
                                                                    'Low',
                                                                    'Close',
                                                                    'Volume',
                                                                    'Close time',
                                                                    'Quote asset volume',
                                                                    'Number of trades',
                                                                    'Taker buy base asset volume',
                                                                    'Taker buy quote asset volume',
                                                                    'Ignore'))

    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')

    return df


def createData(TICKER, DAY, EARLIEST=False):
    PERIOD = TICKER.split("_")[1]
    TICKER = TICKER.split("_")[0]
    timestamp = client._get_earliest_valid_timestamp(TICKER, PERIOD)
    if EARLIEST:
        histData = client.get_historical_klines(TICKER, PERIOD, timestamp)
    else:
        histData = client.get_historical_klines(TICKER, PERIOD, f"{DAY} day ago UTC")
    histData = np.array(histData)
    print(f"Length: {len(histData)}")
    histData = binanceDataFrame(histData)
    histData = histData.drop('Open Time', axis=1)
    histData['Date'] = histData['Close time']
    histData = histData.sort_values(by='Date')
    histData = histData.drop('Close time', axis=1)
    histData = histData.drop('Number of trades', axis=1)
    histData = histData.drop('Quote asset volume', axis=1)
    histData = histData.drop('Taker buy base asset volume', axis=1)
    histData = histData.drop('Taker buy quote asset volume', axis=1)
    histData = histData.drop('Ignore', axis=1)
    histData['Adj Close'] = histData['Close']
    #histData.to_csv(f'./{TICKER}.csv', index=False)
    #print("File saved!")
    return histData


# %%
