import numpy as np
import pandas as pd
import numbers


def downscale_market(market, freq):
    """
    Reduces the time frequency of a market.
    For instance, thie function lets you convert a dataframe containing hourly prices to daily prices.

    Examples of valid frequency values : 'm' for monthly, 'd' for daily, '3h' for every 3 hours, 'min' for every minute...
    """

    resampled_market = pd.DataFrame()

    if 'open' in market.columns:
        resampled_market['open'] = market['open'].resample(freq).first()

    if 'high' in market.columns:
        resampled_market['high'] = market['high'].resample(freq).max()

    if 'low' in market.columns:
        resampled_market['low'] = market['low'].resample(freq).min()

    if 'close' in market.columns:
        resampled_market['close'] = market['close'].resample(freq).last()

    if 'base_volume' in market.columns:
        resampled_market['base_volume'] = market['base_volume'].resample(freq).sum()

    if 'volume' in market.columns:
        resampled_market['volume'] = market['volume'].resample(freq).sum()

    return resampled_market


def add_variation(market, begin=-1, end=0, column='close', fillna=False):
    """
    Add a variation column to the market dataframe. The variation is the ratio between prices at different times.
    By default, the variation is calculated on close prices, from N-1 to N.

    More candles can be included by setting the begin and end value. Theses values are differences between the
    current timeslot and the one to be considered.

    For example, setting begin to 0 and end to 2 will produce the variation between the close prices at N and N+2.
    """

    if begin >= end:
        raise ValueError('begin tick must preceed than end tick')

    c_name = 'var_' + label_time_diff(begin) + "_" + label_time_diff(end)
    shift_begin = market.shift(-begin)
    shift_end = market.shift(-end)

    market[c_name] = shift_end[column] / shift_begin[column]

    if fillna:
        market[c_name].fillna(1, inplace=True)


def strongest_variation(serie, delta):
    """
    For each timestamp, the function associates the strongest variation observed from N to any timestamp between N+1 and N+d_max (or inversely if d_max is negative)
    """

    if delta == 0:
        return serie

    unit = 1 if delta > 0 else -1
    delta = abs(delta)

    variations = pd.Series(np.repeat(0, serie.size), index=serie.index)

    while delta > 0:
        sv = serie.shift(-delta * unit)
        if unit > 0:
            sv = sv / serie
        else:
            sv = serie / sv

        sv -= 1

        maxabs = lambda x: max(x.min(), x.max(), key=abs)
        variations = pd.concat([variations, sv], axis=1).apply(maxabs, axis=1)

        delta -= 1

    return variations + 1


def label(serie, buy_threshold=1.002, sold_threshold=0.998):
    return serie.apply(lambda p: 'B' if p >= buy_threshold else 'S' if p <= sold_threshold else 'H')




def unfold_time_serie(serie, d_max, drop_boundaries=False):
    """
    Transforms a time serie to a dataframe where each line contains the value at a given instant N, then the value N+1, then N+2... until N+d_max
    If d_max is negative, then the value are taken from the past instead of the future (N, N-1, N-2, ... N-d_max)
    """

    past = d_max < 0
    sign = '-' if past else '+'
    val = -1 if past else 1

    cols = []
    colnames = []

    for i in range(0, (val * d_max) + 1):
        cols.append(serie)
        serie = serie.shift(-val)
        colnames.append(label_time_diff(val * i))

    unfolded = pd.concat(cols, axis=1)

    if drop_boundaries:
        if past:
            unfolded.drop(serie.iloc[0:d_max * val].index, inplace=True)
        else:
            unfolded.drop(serie.iloc[-d_max * val:].index, inplace=True)

    # unfolded.dropna(inplace=True)
    unfolded.columns = colnames

    return unfolded


def label_time_diff(d):
    if not isinstance(d, int):
        raise ValueError('d must be an integer')

    label = 'N'
    if d != 0:
        if d > 0:
            label += '+'
        label += str(d)
    return label


def make_sliding_window(market, sequence_size):
    """
    Converts a market dataframe to a 3-dimensional numpy array containing sliding windows of specified size
    """

    market = market.values
    seq = sequence_size
    s0, s1 = market.strides
    points, features = market.shape

    return np.lib.stride_tricks.as_strided(market, shape=(points - seq + 1, seq, features), strides=(s0, s0, s1)).copy()


def binary_trend(variation, neutral='B'):
    """
    Converts a value, a serie or a ndarray of variations, to a binary modality (either B for Buy when variation is greather than 1 or S otherwise).
    """
    return trend(variation, 1, 1, hold_symbol=neutral)


def trend(variation, hold_lower_bound=0.99, hold_upper_bound=1.01, buy_symbol='B', sell_symbol='S', hold_symbol='H'):
    """
    Converts a value, a serie or a ndarray of variations to a modality (either B, S or H). Boundaries can be set with hold_lower_bound and hold_upper_bound.
    """

    if isinstance(variation, numbers.Number):

        if variation <= 0:
            raise ValueError('Variations must be positive numbers.')

        if np.isnan(variation):
            return None

        if variation < hold_lower_bound:
            return sell_symbol
        elif variation > hold_upper_bound:
            return buy_symbol
        else:
            return hold_symbol

    args = locals()
    del args['variation']

    if isinstance(variation, pd.Series):
        return variation.map(lambda v: trend(v, **args))

    if isinstance(variation, np.ndarray):
        return np.vectorize(trend)(variation, **args)

    raise ValueError('Unsupported type for variation (must be a number, a ndarray or pandas Series).')

    


