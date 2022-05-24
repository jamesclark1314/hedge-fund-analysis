# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 13:13:59 2022

@author: James Clark
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import yfinance as yf
import statsmodels.formula.api as smf
import seaborn as sns

portfolio = pd.read_csv('Portfolio_2021.csv')
stocks = pd.read_csv('Stocks_2021.csv')
spdr = pd.read_csv('SPDR.csv')
ff = pd.read_csv('FF.csv')

#Collect daily returns of SPDRs from CRSP.
spdr['Datetime'] = spdr['date'].apply(lambda x: pd.to_datetime(str(x)))
spdr = spdr.pivot_table(index = ["Datetime"], columns = 'TICKER', values = 'PRC'
                        , aggfunc = 'sum')
spdr = spdr.fillna(0)
spdr['SLY'] = spdr['DSC'] + spdr['SLY']
spdr['SLYG'] = spdr['DSG'] + spdr['SLYG']
spdr['SLYV'] = spdr['DSV'] + spdr['SLYV']
spdr['SPYG'] = spdr['ELG'] + spdr['SPYG']
spdr['SPYV'] = spdr['ELV'] + spdr['SPYV']
spdr = spdr.drop(columns = ['DSC','DSG','DSV','ELG','ELV'])
spdr = spdr.pct_change()

# Set a Datetime Index
portfolio['Datetime'] = pd.to_datetime(portfolio['DATE'])
portfolio = portfolio.set_index(['Datetime'])
del portfolio['DATE']

stocks['Datetime'] = pd.to_datetime(stocks['DATE'])
stocks = stocks.set_index(['Datetime'])
del stocks['DATE']

ff['Datetime'] = ff['date'].apply(lambda x: pd.to_datetime(str(x), 
                                  format = '%Y%m%d'))
ff = ff.set_index(['Datetime'])
del ff['date']

ff.columns = ['Full Mkt']

# Import ETF historical data
mkt = yf.Ticker('SPY')
mkt_hist = mkt.history(start = '2010-05-01', end = '2014-01-31')

russ = yf.Ticker('VTHR')
russ_hist = russ.history(start = '2010-05-01', end = '2014-01-31')

russ_val = yf.Ticker('IWN')
russ_val = russ_val.history(start = '2010-05-01', end = '2014-01-31')

russ_grow = yf.Ticker('IWN')
russ_grow = russ_grow.history(start = '2010-05-01', end = '2014-01-31')


# Drop unnecessary columns
del mkt_hist['Dividends']
del mkt_hist['Stock Splits']
del mkt_hist['Volume']
del mkt_hist['Low']
del mkt_hist['High']
del mkt_hist['Open']

mkt_hist.columns = ['Close Price']

del russ_hist['Dividends']
del russ_hist['Stock Splits']
del russ_hist['Volume']
del russ_hist['Low']
del russ_hist['High']
del russ_hist['Open']

russ_hist.columns = ['Close Price']

del russ_val['Dividends']
del russ_val['Stock Splits']
del russ_val['Volume']
del russ_val['Low']
del russ_val['High']
del russ_val['Open']

russ_val.columns = ['Close Price']

del russ_grow['Dividends']
del russ_grow['Stock Splits']
del russ_grow['Volume']
del russ_grow['Low']
del russ_grow['High']
del russ_grow['Open']

russ_grow.columns = ['Close Price']

# Calculate returns
mkt_hist['Mkt Ret'] = mkt_hist.pct_change()
russ_hist['Russ Ret'] = russ_hist.pct_change()
russ_val['Russ Val Ret'] = russ_val.pct_change()
russ_grow['Russ Grow Ret'] = russ_grow.pct_change()

# Create dataframe for returns of market and portfolio
all_rets = mkt_hist.merge(portfolio['ret2'], how = 'left', 
                                  left_index = True, right_index = True)
all_rets = all_rets.merge(portfolio['ret3'], how = 'left', 
                                  left_index = True, right_index = True)
all_rets = all_rets.merge(russ_hist['Russ Ret'], how = 'left', 
                                  left_index = True, right_index = True)
all_rets = all_rets.merge(russ_val['Russ Val Ret'], how = 'left', 
                                  left_index = True, right_index = True)
all_rets = all_rets.merge(russ_grow['Russ Grow Ret'], how = 'left', 
                                  left_index = True, right_index = True)
all_rets = all_rets.merge(ff['Full Mkt'], how = 'left', 
                                  left_index = True, right_index = True)

# Adding ret2 and ret3 to spdr dataframe
spdr = spdr.merge(all_rets['ret2'], how = 'left', 
                                  left_index = True, right_index = True)
spdr = spdr.merge(all_rets['ret3'], how = 'left', 
                                  left_index = True, right_index = True)

# Calculate cumulative returns
all_rets['Mkt Cum Ret'] = (1 + all_rets['Mkt Ret']).cumprod() - 1
all_rets['ret2 cum ret'] = (1 + all_rets['ret2']).cumprod() - 1
all_rets['ret3 cum ret'] = (1 + all_rets['ret3']).cumprod() - 1
all_rets['Russ Cum Ret'] = (1 + all_rets['Russ Ret']).cumprod() - 1
all_rets['Full Mkt cum ret'] = (1 + all_rets['Russ Ret']).cumprod() - 1

# Plot the cumulative return series 
all_rets.plot(y = ['Mkt Cum Ret', 'ret2 cum ret', 'ret3 cum ret', 'Russ Cum Ret'])
plt.title('Cumulative Returns')
plt.show()

# Examine the risk profile of the fund vs the market index

# Means
mkt_mean = all_rets['Mkt Ret'].mean() * 252
ret2_mean = all_rets['ret2'].mean() * 252
ret3_mean = all_rets['ret3'].mean() * 252
russ_mean = all_rets['Russ Ret'].mean() * 252

# Stdev
mkt_stdev = all_rets['Mkt Ret'].std() * math.sqrt(252)
ret2_stdev = all_rets['ret2'].std() * math.sqrt(252)
ret3_stdev = all_rets['ret3'].std() * math.sqrt(252)
russ_stdev = all_rets['Russ Ret'].std() * math.sqrt(252)

# Sharpe
mkt_sharpe = mkt_mean / mkt_stdev
ret2_sharpe = ret2_mean / ret2_stdev
ret3_sharpe = ret3_mean / ret3_stdev
russ_sharpe = russ_mean / russ_stdev

# Regression
ret2_regress = smf.ols('Q("ret2") ~ Q("Mkt Ret")',
                          data = all_rets).fit()
ret3_regress = smf.ols('Q("ret3") ~ Q("Mkt Ret")',
                          data = all_rets).fit()
russ_regress = smf.ols('Q("Russ Ret") ~ Q("Mkt Ret")',
                          data = all_rets).fit()
russ_val_regress = smf.ols('Q("ret2") ~ Q("Russ Val Ret")',
                          data = all_rets).fit()
russ_grow_regress = smf.ols('Q("ret2") ~ Q("Russ Grow Ret")',
                          data = all_rets).fit()

risk_data = {'Mean': [mkt_mean, ret2_mean, ret3_mean, russ_mean],
             'Stdev': [mkt_stdev, ret2_stdev, ret3_stdev, russ_stdev],
             'Sharpe': [mkt_sharpe, ret2_sharpe, ret3_sharpe, russ_sharpe],
             'Beta': [1, ret2_regress.params['Q("Mkt Ret")'], 
                      ret3_regress.params['Q("Mkt Ret")'],
                      russ_regress.params['Q("Mkt Ret")']]}

risk_stats = pd.DataFrame(risk_data, index = ['Mkt', 'ret2', 'ret3', 'Russ'])

# Regression plot
sns.regplot(x = 'Mkt Ret', y = 'ret2', data = all_rets)
# sns.regplot(x = 'Mkt Ret', y = 'ret3', data = all_rets)
# sns.regplot(x = 'Mkt Ret', y = 'Russ Ret', data = all_rets)
# sns.regplot(x = 'Russ Ret', y = 'ret2', data = all_rets)
# sns.regplot(x = 'Russ Val Ret', y = 'ret2', data = all_rets)
# sns.regplot(x = 'Russ Grow Ret', y = 'ret2', data = all_rets)


# Muliple regression from sector ETFs
ret2_industry = smf.ols(
    'Q("ret2") ~ Q("XLB") + Q("XLV") + Q("XLP") + Q("XLY") + Q("XLE") + Q("XLF") + Q("XLI") + Q("XLK") + Q("XLU")'
    , data = spdr).fit()
ret3_industry = smf.ols(
    'Q("ret3") ~ Q("XLB") + Q("XLV") + Q("XLP") + Q("XLY") + Q("XLE") + Q("XLF") + Q("XLI") + Q("XLK") + Q("XLU")'
    , data = spdr).fit()

# Multiple regression from factor ETFs
ret2_factor = smf.ols(
    'Q("ret2") ~ Q("SLY") + Q("SLYG") + Q("SLYV") + Q("SPY") + Q("SPYG") + Q("SPYV")'
    , data = spdr).fit()
ret3_factor = smf.ols(
    'Q("ret3") ~ Q("SLY") + Q("SLYG") + Q("SLYV") + Q("SPY") + Q("SPYG") + Q("SPYV")'
    , data = spdr).fit()

# Single Regressions

ret2_russ = smf.ols('Q("ret2") ~ Q("Russ Ret")', data = all_rets).fit()
ret2_spy = smf.ols('Q("ret2") ~ Q("Mkt Ret")', data = all_rets).fit()

# Industry ETFs 
materials = smf.ols('Q("ret2") ~ Q("XLB")', data = spdr).fit()
healthcare = smf.ols('Q("ret2") ~ Q("XLV")', data = spdr).fit()
consumer_stap = smf.ols('Q("ret2") ~ Q("XLP")', data = spdr).fit()
consumer_disc = smf.ols('Q("ret2") ~ Q("XLY")', data = spdr).fit()
energy = smf.ols('Q("ret2") ~ Q("XLE")', data = spdr).fit()
financial = smf.ols('Q("ret2") ~ Q("XLF")', data = spdr).fit()
industrial = smf.ols('Q("ret2") ~ Q("XLI")', data = spdr).fit()
tech = smf.ols('Q("ret2") ~ Q("XLK")', data = spdr).fit()
utilities = smf.ols('Q("ret2") ~ Q("XLU")', data = spdr).fit()

# Factor ETFs
sly = smf.ols('Q("ret2") ~ Q("SLY")', data = spdr).fit()
slyg = smf.ols('Q("ret2") ~ Q("SLYG")', data = spdr).fit()
slyv = smf.ols('Q("ret2") ~ Q("SLYV")', data = spdr).fit()
spy = smf.ols('Q("ret2") ~ Q("SPY")', data = spdr).fit()
spyg = smf.ols('Q("ret2") ~ Q("SPYG")', data = spdr).fit()
spyv = smf.ols('Q("ret2") ~ Q("SPYV")', data = spdr).fit()

# Output to CSV
risk_stats.to_csv('Risk Stats.csv')

stdsmallgrow = spdr['SLYG'].std() * math.sqrt(252)
stdlargegrow = spdr['SPYG'].std() * math.sqrt(252)

midcap = yf.download(['VOT', 'VOE','VO'], start = '2010-01-07', end = '2014-02-01')

del midcap['Close']
del midcap['High']
del midcap['Low']
del midcap['Open']
del midcap['Volume']

midcap.columns = ['VOT', 'VOE', 'VO']
midcap = midcap.pct_change()

spdr = spdr.merge(midcap['VOT'], how = 'left', 
                                  left_index = True, right_index = True)
spdr = spdr.merge(midcap['VOE'], how = 'left', 
                                  left_index = True, right_index = True)
spdr = spdr.merge(midcap['VO'], how = 'left', 
                                  left_index = True, right_index = True)

multi_fact = smf.ols(
    'Q("ret2") ~ Q("VOT") + Q("SLYG") + Q("SLYV") + Q("VOE") + Q("SPYG") + Q("SPYV")'
    , data = spdr).fit()

vot = smf.ols('Q("ret2") ~ Q("VOT")', data = spdr).fit()
voe = smf.ols('Q("ret2") ~ Q("VOE")', data = spdr).fit()
vo = smf.ols('Q("ret2") ~ Q("VO")', data = spdr).fit()

# Try a bunch of regressions fml
try1 = smf.ols(
    'Q("ret2") ~ Q("VOT") + Q("SLYV") + Q("SPYG") + Q("VOE")'
    , data = spdr).fit()
try2 = smf.ols(
    'Q("ret2") ~ Q("VOT") + Q("VOE")'
    , data = spdr).fit()
try3 = smf.ols(
    'Q("ret2") ~ Q("VOT") + Q("SLYG") + Q("VOE") + Q("SPYV") + Q("SLY") + Q("SPY")'
    , data = spdr).fit()

# Adjust for 2% annual management fee
fees = all_rets['ret2'] - (0.02/252)

# fees stats
fee_mean = fees.mean() * 252
fee_stdev = fees.std() * math.sqrt(252)
fee_sharpe = fee_mean / fee_stdev

# Merge fees into all_rets
fees = pd.DataFrame(fees)
fees.columns = ['Fee Ret']
all_rets = all_rets.merge(fees, how = 'left', 
                                  left_index = True, right_index = True)

# Resample monthly
all_rets_month = all_rets.resample('M').agg(lambda r: (r + 1).prod()- 1)

# Plot fees vs spy
all_rets_month.plot(y = ['Fee Ret', 'Mkt Ret'])
plt.show()

# High water mark
# all_rets['HWM'] = all_rets['ret2 cum ret'].cummax()

# Function to slice date range
def imsmart(start, end):
    
    global resamp
    resamp = all_rets[start:end]
    resamp['HWM'] = resamp['ret2 cum ret'].cummax()
    return resamp
    
a = imsmart('2010-05-03','2010-12-31')
ab = imsmart('2011-01-01','2011-12-31')
abc = imsmart('2012-01-01','2012-12-31')
abcd = imsmart('2013-01-01','2013-12-31')

# Calculate 20% fee above HWM
all_rets['Final Ret'] = all_rets['Fee Ret'] * 0.8

# Cumulative returns
all_rets['Fee Adjusted Ret'] = (1 + all_rets['Final Ret']).cumprod() - 1

# Plot new cumulative returns
all_rets.plot(y = ['Fee Adjusted Ret', 'ret2 cum ret', 'Full Mkt cum ret'])
plt.title('Cumulative Returns')
plt.show()

# New stats
fee_mean = all_rets['Final Ret'].mean() * 252
ffmkt_mean = all_rets['Full Mkt'].mean() * 252

fee_stdev = all_rets['Final Ret'].std() * math.sqrt(252)
ffmkt_stdev = all_rets['Full Mkt'].std() * math.sqrt(252)

fee_sharpe = fee_mean / fee_stdev
ffmkt_sharpe = ffmkt_mean / ffmkt_stdev

