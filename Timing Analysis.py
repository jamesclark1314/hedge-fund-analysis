# -*- coding: utf-8 -*-
"""
Created on Mon May 16 16:50:48 2022

@author: James Clark
"""

import pandas as pd
import numpy as np
import yfinance as yf
import seaborn as sns

data = pd.read_csv('NOUSETHISONE.csv')
data['Style'] = data['Style'].replace(['Midcap Grow'], 'VOT')
data['Style'] = data['Style'].replace(['Midcap Val'], 'VOE')

# Import ETF historical data for sector
sector = yf.download(['XLB', 'XLV', 'XLP', 'XLY', 'XLE', 'XLF', 'XLI', 'XLK',
                      'XLU'], start = '2011-05-03', end = '2014-02-01')
del sector['Close']
del sector['High']
del sector['Low']
del sector['Open']
del sector['Volume']

sector.columns = ['XLB', 'XLV', 'XLP', 'XLY', 'XLE', 'XLF', 'XLI', 'XLK', 'XLU']

sector = sector.pct_change()

# Import ETF historical data for style
style = yf.download(['SLYG', 'SPYG', 'SLYV', 'SPYV', 'VOT', 'VOE', 'VO', 'SPY', 'SLY'],
                    start = '2010-01-07', end = '2014-02-01')
del style['Close']
del style['High']
del style['Low']
del style['Open']
del style['Volume']

style.columns = ['SLYG', 'SPYG', 'SLYV', 'SPYV', 'VOT', 'VOE', 'VO', 'SPY', 'SLY']

style = style.pct_change()

# Ticker Returns
data['Datetime'] = pd.to_datetime(data['DATE'])
data = data.set_index(['Datetime'])
del data['DATE']

# Sector function
def sectfunc(ticker):
    df = data.loc[data['Sector'] == ticker]
    df = df.groupby(df.index)['AbsSecRet'].mean()
    df = pd.DataFrame(df)
    df.columns = [ticker + 'Tick']
    
    df = df.merge(sector[ticker], how = 'left', 
                                  left_index = True, right_index = True)
    
    sns.regplot(x = ticker, y = ticker + 'Tick', data = df)

sectfunc('XLU')

# Style function
def stylefunc(ticker):
    
    df = data.loc[data['Style'] == ticker]
    df = df.groupby(df.index)['AbsSecRet'].mean()
    df = pd.DataFrame(df)
    df.columns = [ticker + 'Tick']
        
    df = df.merge(style[ticker], how = 'left', 
                                  left_index = True, right_index = True)
    
    # df[f"{df.columns[0]}"] = np.log(df[f"{df.columns[0]}"])
    # df[f"{df.columns[1]}"] = np.log(df[f"{df.columns[1]}"])
    
    sns.regplot(x = ticker, y = ticker + 'Tick', data = df)
    
# stylefunc('VOE')

# Sort by mcap
data['Type'] = np.where(data['mcap'] >= 1000000, 'SPY', 
                        (np.where(data['mcap'] <= 200000,
                                  'SLY', 'VO')))

def sizefunc(ticker):
    df = data.loc[data['Type'] == ticker]
    df = df.groupby(df.index)['AbsSecRet'].mean()
    df = pd.DataFrame(df)
    df.columns = [ticker + 'Tick']
        
    df = df.merge(style[ticker], how = 'left', 
                                  left_index = True, right_index = True)
        
    sns.regplot(x = ticker, y = ticker + 'Tick', data = df)
    
# sizefunc('SLY')
