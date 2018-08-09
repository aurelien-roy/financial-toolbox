import numpy as np
import pandas as pd
from pandas.tseries.frequencies import to_offset

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


def add_variation(market, begin=-1, end=0, column='close'):

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

	for i in range(0, (val * d_max)+1):
		cols.append(serie)
		serie = serie.shift(-val)
		colnames.append(label_time_diff(val * i))

	unfolded = pd.concat(cols, axis=1)
    
	if drop_boundaries:
		if past:
			unfolded.drop(serie.iloc[0:d_max*val].index, inplace=True)
		else:
			unfolded.drop(serie.iloc[-d_max*val:].index, inplace=True)
        
    #unfolded.dropna(inplace=True)
	unfolded.columns = colnames
	
	return unfolded


def label_time_diff(d):

	if not isinstance(d, int):
		raise ValueError('d must be an integer')

	label = 'N'
	if d != 0:
		label += str(d)
	return label


def make_sliding_window(market, sequence_size):

	"""
	Convert a market dataframe to a 3-dimensional numpy array containing sliding windows of specified size
	"""

	market = market.values
	seq = sequence_size
	s0, s1 = market.strides
	points, features = market.shape

	return np.lib.stride_tricks.as_strided(market, shape=(points - seq + 1, seq, features), strides=(s0, s0, s1)).copy()
