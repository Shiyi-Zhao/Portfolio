# -*- coding: utf-8 -*-
"""

Description: calculate snowball option winrate based on historical data.

Note: Sensitive information has been obfuscated.

"""

''' import and preprocessing'''
import pandas as pd
import numpy as np
from WindPy import *
import datetime as dt
from dateutil.relativedelta import relativedelta
from scipy.stats import norm
import matplotlib.pyplot as plt
w.start()

code = '000905.SH' 

#close price 20100101-20220731
close = w.wsd(code, "close", "2010-01-01", "2022-07-31", "")
CSI1000_close = pd.DataFrame(data=close.Data,index=close.Codes,columns=close.Times).T.reset_index()
CSI1000_close = CSI1000_close.rename(columns={'index': 'Date','000852.SH':'Price'})
CSI1000_close['Date'] = pd.to_datetime(CSI1000_close.Date)

# trading days 20100101-20200729
trade = w.tdays("2010-01-01", "2020-07-29", "")
trade_days = pd.DataFrame(data=trade.Data,index=['Date']).T


def find_tradedate(dte,CSI1000_close): 
    if len(CSI1000_close[CSI1000_close['Date'] == dte]) == 1:
        dte_trade = dte
    else:
        dte_trade = CSI1000_close[CSI1000_close['Date'] > dte].iloc[0,0]
    return dte_trade

def get_payment(knock_out_rate,knock_in_rate,r_fixed):
    try:
        knock_out = min(knock_out_observe_pd[knock_out_observe_pd['Price']>price_out].index)
        knock_out_date = close_i.iloc[knock_out,0]
        knock_out_price = close_i.iloc[knock_out,1]
        payment = r_fixed*(knock_out_date-trade_day).days/365
    except:
        try:
            knock_in = min(close_i[close_i['Price']< price_in].index)
            price_24mlater = close_i.iloc[-1,1]
            payment = min(0,price_24mlater/trade_price-1)            
        except:
            payment = r_fixed
    return payment

def get_win_status(payment):
    if payment > 0:
        if_win = 1
    else:
        if_win = 0
    return if_win

'''set knock in and knock out barrier'''
knock_out_array = np.arange(1,1.05,0.01)
knock_in_array = np.arange(0.6,0.8,0.05)
lock_month = 3
r_fixed = 0.12

'''calculation'''
win_list_all = []
for knock_in_rate in knock_in_array:
    print(knock_in_rate)
    win_list_out = []
    for knock_out_rate in knock_out_array:
        print(knock_out_rate)
        payment_list = []
        #i=0
        for i in range(len(trade_days)):
            #print(i)
            trade_day = trade_days.iloc[i,0]
            trade_price = CSI1000_close[CSI1000_close['Date']==trade_day].iloc[0,1]
            
            knock_out_observe = []
            day_3mlater = trade_day+relativedelta(months=lock_month)
            day_3mlater_trade = find_tradedate(day_3mlater,CSI1000_close)
            day_3mlater_price = CSI1000_close[CSI1000_close['Date'] == day_3mlater_trade].iloc[0,1]
            knock_out_observe.append([day_3mlater_trade,day_3mlater_price])
            day_24mlater = trade_day+relativedelta(months=24)
            day_24mlater_trade = find_tradedate(day_24mlater,CSI1000_close)
            for j in range(21):
                j+=1
                day_nlater = day_3mlater+relativedelta(months=j)
                day_nlater_trade = find_tradedate(day_nlater,CSI1000_close)
                day_nlater_price = CSI1000_close[CSI1000_close['Date'] == day_nlater_trade].iloc[0,1]
                knock_out_observe.append([day_nlater_trade,day_nlater_price])
            knock_out_observe_pd = pd.DataFrame(knock_out_observe,columns=['Date','Price'])
            
            close_i = CSI1000_close[(CSI1000_close['Date'] <= day_24mlater_trade) & (CSI1000_close['Date'] >= day_3mlater_trade)].reset_index(drop=True)
            price_in = knock_in_rate * trade_price
            price_out = knock_out_rate * trade_price
            payment = get_payment(knock_out_rate,knock_in_rate,r_fixed)
            if_win = get_win_status(payment)
            payment_list.append([trade_day,payment,if_win])
        
        payment_pd = pd.DataFrame(payment_list,columns=['Date','return','if_win'])
        win_p = payment_pd['if_win'].sum()/payment_pd['if_win'].count()
        win_list_out.append(win_p)
        plt.plot(payment_pd.iloc[:,0],payment_pd.iloc[:,1])
        title = "knock_in="+str(knock_in_rate*100)+"% knock_out="+str(knock_out_rate*100)+"% Historical Return"
        plt.title(title)
        plt.savefig(title+".png")
    win_list_all.append(win_list_out)
    
win_pd = pd.DataFrame(win_list_all,index=knock_in_array,columns=knock_out_array)
print(win_pd)
    





