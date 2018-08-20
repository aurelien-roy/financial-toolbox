import pandas as pd
import numpy as np
import operator


def market_from_csv(
        filename,
        cols={'time': 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4, 'base_volume': 5, 'volume': 6},
        skiprows=0,
        sep=',',
        time_format=None
):
    """
    Read a CSV file where each line matches a market candle.
    The file must at least contains timestamps and close prices.
    Open, High, Low, Base Volume and Volume are also supported.

    :return: A pandas dataframe filled with the market data.
    """

    _valid_cols = ['time', 'open', 'high', 'low', 'close', 'base_volume', 'volume']

    if not all([k in _valid_cols for k in cols]):
        raise ValueError("cols contains unknown column type. Valid values are " + ",".join(_valid_cols))

    if len(cols.values()) != len(set(cols.values())):
        raise ValueError("cols contains duplicates column indexes")

    if 'time' not in cols.keys():
        raise ValueError("time column must be present")

    if 'close' not in cols.keys():
        raise ValueError("closing price column must be present")

    sorted_cols = sorted(cols.items(), key=operator.itemgetter(1))
    colnames = list(map(lambda x: x[0], sorted_cols))

    ticker = pd.read_csv(
        filename,
        sep=sep,
        skiprows=skiprows,
        usecols=cols.values(),
        header=None,
        names=colnames
    )

    ticker = ticker[[c for c in _valid_cols if c in colnames]]

    if time_format is not None or ticker.time.dtype == np.int64:
        ticker.index = pd.to_datetime(ticker.time, unit='s')
    else:
        ticker.index = pd.to_datetime(ticker.time, format=time_format)

    ticker.drop("time", axis=1, inplace=True)

    return ticker
