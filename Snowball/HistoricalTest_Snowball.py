# -*- coding: utf-8 -*-
"""

Description: calculate historical income distribution of snowball option.

Note: Sensitive information has been obfuscated.

"""

from WindPy import *
w.start()
import numpy as np
import datetime as dt
import time
from pandas import DataFrame as df
from dateutil.relativedelta import relativedelta
#%%
'''Standard Parameters'''
ko_barrier=1.00  # knock out price
d_ko=-0.000  # the change to the knock out price, positive is increasing, negative is decreasing
ko_rebate=0.23  # knock out yield (annualized)
ki_barrier=0.70  # knock in price
ki_strike=1  # strike price after knocking in
startmm=3  # observation start month
endmm=24  # observation end month
ko_obsv=list(np.linspace(startmm,endmm,endmm-startmm+1))
'''Protection/Margin Parameters'''
max_loss=1.00  # e.g. 70% of the principle would be protected, then max_loss=0.30; no protection, max_loss=1.00
margin=1.00  # e.g. 2x leverage, margin=1/2
'''Advance Hedging Parameters'''
ra_month=np.array([])  # e.g. np.array([6,12]); np.array([])
ra_barrier=np.array([])  # corresponding barrier price, e.g.np.array([0.85,0.80])；np.array([])
'''Knock-out Enhancement Parameters'''
ehc_kopr=0  # After knocking out, the participation rate of the increase part
#%%
'''Historical Backtest Parameters'''
date_start=dt.date(2010,1,1) # backtest start date
date_end=dt.date.today()-dt.timedelta(days=int(endmm/12*365)+1)  # backtest end date
code="000852.SH"  # code
#%%
'''Get Data'''
data=w.wsd(code,'close',date_start,dt.date.today(),"PriceAdj=F")
times=data.Times
price=data.Data[0]
output=df(price,index=times,columns=list(['price']))
'''Date Transfer'''
time_stamp=np.zeros(len(times))
for i,t in enumerate(times):
    time_stamp[i]=datetime.strptime(str(t)+' 00:00:00', '%Y-%m-%d %H:%M:%S').timestamp()
'''Backtest'''
for t in times:
    #t = times[0]
    if t>=date_end:
        break
    obsv_date=list()
    for i in ko_obsv:
        obsv_date.append(np.array(times)[time_stamp-datetime.strptime(str(t+relativedelta(months=+int(i)))+' 00:00:00', '%Y-%m-%d %H:%M:%S').timestamp()>0][0])
    for index, t_obsv in enumerate(obsv_date):
        price_obsv=output.loc[t:t_obsv,'price']
        output.loc[t,'is_ki']=False
        output.loc[t,'is_ko']=False
        output.loc[t,'is_ra']=False
        output.loc[t,'ko_month']=0
        output.loc[t,'ra_month']=0
        if min(price_obsv)/price_obsv.iloc[0]<ki_barrier:  #if knock in
            output.loc[t,'is_ki']=True
        if price_obsv.iloc[-1]/price_obsv.iloc[0]>ko_barrier+d_ko*index:  #if knock out
            output.loc[t,'is_ko']=True
            output.loc[t,'ko_month']=ko_obsv[index]
            output.loc[t,'payoff']=ko_rebate*((t_obsv-t).days+1)/365+ehc_kopr*(price_obsv.iloc[-1]/price_obsv.iloc[0]-ki_strike)
            if output.loc[t,'is_ki']==True:
                output.loc[t,'flag']='kiko'
            else:
                output.loc[t,'flag']='ko'
            break
        if sum(ko_obsv[index]==ra_month)>0 and min(price_obsv)/price_obsv.iloc[0]>ra_barrier[list(ra_month).index(ko_obsv[index])]:  
            #advance hedging
            output.loc[t,'is_ra']=True
            output.loc[t,'ra_month']=ko_obsv[index]
            output.loc[t,'payoff']=ko_rebate*((t_obsv-t).days+1)/365
            if output.loc[t,'is_ki']==True:
                output.loc[t,'flag']='kira'
            else:
                output.loc[t,'flag']='ra'
            break
        if ko_obsv[index]==endmm:
            if output.loc[t,'is_ki']==True:
                output.loc[t,'payoff']=max(-max_loss,(price_obsv.iloc[-1]/price_obsv.iloc[0]-ki_strike)/margin)
                output.loc[t,'flag']='ki'
            else:
                output.loc[t,'payoff']=ko_rebate*((t_obsv-t).days+1)/365
                output.loc[t,'flag']='none'
                output.loc[t,'ko_month']=endmm
output=output.drop(index=output.loc[t:,:].index)
#%%
'''Statistics'''
input_index=list(['ko_barrier','d_ko','ko_rebate','ki_barrier','ki_strike','startmm','endmm','max_loss','margin','ra_month','ra_barrier','ehc_kopr'])
input_params=df(list([ko_barrier,d_ko,ko_rebate,ki_barrier,ki_strike,startmm,endmm,max_loss,margin,ra_month,ra_barrier,ehc_kopr]),index=input_index,columns=list(['params']))



