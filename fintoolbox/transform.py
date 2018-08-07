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


def add_variation(market):
	market['variation'] = market['close'] / market['open']

	return market


def add_label(market, buy_threshold=1.002, sold_threshold=0.998):

	if 'variation' not in market:
		add_variation(market)

	serie = market['variation']

	market['label'] = serie.apply(lambda p: 'B' if p >= buy_threshold else 'S' if p <= sold_threshold else 'H')

	return market


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
        
		name = 'N'
        
		if i != 0:
			name += sign + str(i)
        
		colnames.append(name)

	unfolded = pd.concat(cols, axis=1)
    
	if drop_boundaries:
		if past:
			unfolded.drop(serie.iloc[0:d_max*val].index, inplace=True)
		else:
			unfolded.drop(serie.iloc[-d_max*val:].index, inplace=True)
        
    #unfolded.dropna(inplace=True)
	unfolded.columns = colnames
	
	return unfolded
