import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_finance import candlestick_ohlc
from matplotlib.collections import PolyCollection


def plot_candles(market, width=40, height=50, plot_volume=True):
    """
    Plots a candlestick chart of the specified market dataframe
    """

    plot_index = mdates.date2num(market.index.to_pydatetime())
    cols = ['open', 'high', 'low', 'close']

    if plot_volume:
        if 'volume' in market:
            cols.append('volume')
        else:
            raise ValueError('Unable to find volume column on dataframe. Try to set plot_volume to False')

    # Data preparation
    ohlc = market[cols]
    ohlc.insert(0, 'time', plot_index)

    # Figure initialization
    fig, ax1 = plt.subplots(figsize=(width, height))

    if plot_volume:
        ax2 = ax1.twinx()

    ax1.set_ylabel('Price', fontsize=10)
    ax1.set_xlabel('Time', fontsize=10)

    candlestick_ohlc(ax1, ohlc.values, width=1, colorup='lightgreen', colordown='red')

    # Find most appropriate labelling
    time_format = _find_time_format(market.index)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter(time_format))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=20)

    if plot_volume:
        delta = 0.5
        bars = [((time - delta, 0), (time - delta, vol), (time + delta, vol), (time + delta, 0))
                for time, vol in zip(ohlc['time'], ohlc['volume'])]


        barCollection = PolyCollection(bars,
                                       linewidths=(1,),
                                       facecolors='grey'
                                       )

        ax2.add_collection(barCollection)

        pad = 0.25
        yl = ax1.get_ylim()
        ax1.set_ylim(yl[0] - (yl[1] - yl[0]) * pad, yl[1])

        ax2.autoscale_view()

        yl = ax2.get_ylim()
        ax2.set_ylim(yl[0], yl[1]*(1/pad))
        ax2.yaxis.set_major_formatter(plt.NullFormatter())

    plt.show()


def _find_time_format(times):

    time_interval = (times[-1].timestamp() - times[0].timestamp()) /times.size

    if time_interval < (60*60):
        time_format = '%H:%M'
    elif time_interval < (60*60*24):
        time_format = '%m-%d %H'
    elif time_interval < (60*60*24*29):
        time_format = '%Y-%m-%d'
    elif time_interval < (60*60*24*364):
        time_format = '%Y-%m'
    else:
        time_format = '%Y'

    return time_format