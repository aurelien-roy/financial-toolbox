import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates


def plot_candles(market, width=40, height=50):
    """
    Plots a candlestick chart of the specified market dataframe
    """

    ohlc = market[['open', 'high', 'low', 'close']]
    ohlc.insert(0, 'time', mdates.date2num(market.index.to_pydatetime()))
    f1, ax = plt.subplots(figsize=(width, height))
    candlestick_ohlc(ax, ohlc.values, width=0.3, colorup='lightgreen', colordown='red')

    # Find most appropriate labelling

    idx = market.index
    avg_interval = (idx[-1].timestamp() - idx[0].timestamp()) / idx.size

    if avg_interval < (60*60):
        time_format = '%H:%M'
    elif avg_interval < (60*60*24):
        time_format = '%m-%d %H'
    elif avg_interval < (60*60*24*29):
        time_format = '%Y-%m-%d'
    elif avg_interval < (60*60*24*364):
        time_format = '%Y-%m'
    else:
        time_format = '%Y'

    ax.xaxis.set_major_formatter(mdates.DateFormatter(time_format))
    plt.show()

