# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 13:25:16 2022

@author: James Clark
"""

import pandas as pd
import numpy as np

moesad = pd.read_csv('moesad.csv')
mcap = pd.read_csv('mcap.csv')

# Set a Datetime Index
moesad['Datetime'] = pd.to_datetime(moesad['public_date'])
moesad = moesad.set_index(['Datetime'])

mcap['Datetime'] = pd.to_datetime(mcap['DATE'])
mcap = mcap.set_index(['Datetime'])

del moesad['public_date']
del mcap['DATE']

# Create dataframe for moesad
pivot = moesad.pivot_table(index=["Datetime"], columns='TICKER', values='price-book')
pivot = pd.DataFrame(pivot.mean())
pivot.columns = ['Avg P/B']
pivot.reset_index(inplace = True)

# Sort by style
pivot['Style'] = np.where(pivot['Avg P/B'] > 1, 'Growth', 'Value')

growth = pd.DataFrame(pivot.loc[pivot['Style'] == 'Growth', 'TICKER'])

value = pd.DataFrame(pivot.loc[pivot['Style'] == 'Value', 'TICKER'])


# Create dataframe for mcap
mcap =  mcap.pivot_table(index=["Datetime"], columns='ticker', values='mcap')
mcap = pd.DataFrame(mcap.mean())
mcap.columns = ['Avg Mcap']
mcap.reset_index(inplace = True)

# Sort by mcap
mcap['Type'] = np.where(mcap['Avg Mcap'] >= 1000000, 'Large Cap', 
                        (np.where(mcap['Avg Mcap'] <= 200000,
                                  'Small Cap', 'Mid Cap')))

largecap = mcap.loc[mcap['Type'] == 'Large Cap', 'ticker']
midcap = mcap.loc[mcap['Type'] == 'Mid Cap', 'ticker']
smolcap = mcap.loc[mcap['Type'] == 'Small Cap', 'ticker']

largecap = largecap.to_frame()
smolcap = smolcap.to_frame()
midcap = midcap.to_frame()

# is it a growth and smol cap?
slyg = smolcap.assign(gandsm = smolcap.ticker.isin(growth.TICKER).astype(int))
slyg = slyg.loc[slyg['gandsm'] == 1, 'ticker']
# is it a growth and lg cap?
spyg = largecap.assign(gandlg = largecap.ticker.isin(growth.TICKER).astype(int))
spyg = spyg.loc[spyg['gandlg'] == 1, 'ticker']
# is it a value and smol cap?
slyv = smolcap.assign(gandsm = smolcap.ticker.isin(value.TICKER).astype(int))
slyv = slyv.loc[slyv['gandsm'] == 1, 'ticker']
# is it a value and lg cap?
spyv = largecap.assign(gandlg = largecap.ticker.isin(value.TICKER).astype(int))
spyv = spyv.loc[spyv['gandlg'] == 1, 'ticker']
# is it growth and mid cap?
midgrow = midcap.assign(gandmid = midcap.ticker.isin(growth.TICKER).astype(int))
midgrow = midgrow.loc[midgrow['gandmid'] == 1, 'ticker']
# is it value and mid cap
midval = midcap.assign(gandmid = midcap.ticker.isin(value.TICKER).astype(int))
midval = midval.loc[midval['gandmid'] == 1, 'ticker']
    
# CSV outputs
growth.to_csv('Growth.csv')
value.to_csv('Value.csv')
largecap.to_csv('Large Cap.csv')
midcap.to_csv('Mid Cap.csv')
smolcap.to_csv('Small Cap.csv')



