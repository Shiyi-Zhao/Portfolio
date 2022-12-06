# -*- coding: utf-8 -*-
"""

Description: Pick stocks with strong growth indicators. 

Basic filtering:
1. Net Income TTM growth rate: top 1/3
2. deducted profit/net profit>50%
3. roe>0.01
4. currentratio >-1
5. trade volumne top 90% in the past half year
6. not ST

Scoring:
1. choose the reporting dates as the date changing positions, the return in the past month could represent the market reaction.
2. analyst expectation change
3. analyst agreed expected growth rate

"""

'''import'''

import os
import pandas as pd
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta
from sklearn import preprocessing as prep
import matplotlib.pyplot as plt
from WindPy import *
w.start()

'''get basic pool'''
 
def get_basic_pool(test_date:date):
    """
    
    Parameters
    ----------
    test_date : date
        the begin date of a new time period to change positions

    Returns
    -------
    basic_pool_list: Series
        the list of the basic pool

    """
    
    test_date_last = test_date+relativedelta(years=-1)
    
    whole_mkt = w.wset("listedsecuritygeneralview","sectorid=a001010100000000;field=wind_code,sec_name,trade_status,ipo_date")
    stock_list = pd.DataFrame(whole_mkt.Data).T
    stock_list.columns = ['windcode','name','tradestatus','listdate']
    
    stock_list_i = stock_list[stock_list["listdate"] < pd.to_datetime(test_date)]['windcode']
    netincomeTTM = w.wss(list(stock_list_i), "fa_nppcgr_ttm","tradeDate="+str(test_date))
    netincomeTTMlast = w.wss(list(stock_list_i), "fa_nppcgr_ttm","tradeDate="+str(test_date_last))
    NIgrowth_list = pd.DataFrame(netincomeTTM.Data,index = ["NetIncomeGrowth"],columns = netincomeTTM.Codes).T.reset_index()
    n = int(stock_list_i.shape[0]/3)
    NIgrowthlast_list = pd.DataFrame(netincomeTTMlast.Data,index = ["NetIncomeGrowthlast"],columns = netincomeTTMlast.Codes).T.reset_index()
    filter_code = NIgrowth_list.sort_values("NetIncomeGrowth",ascending=False)[:n]
    ac_code = filter_code.merge(NIgrowthlast_list,how='left',on='index')
    ac_code.eval('ac_rate = (NetIncomeGrowth - NetIncomeGrowthlast)/abs(NetIncomeGrowthlast)', inplace = True)
    m = int(ac_code.shape[0]/2)
    ac_filtered = ac_code.sort_values("ac_rate",ascending=False)[:m]
    
    #no equity fund raising in a recent year
    fundDate = w.wss(list(ac_filtered["index"]), "fellow_listeddate,rightsissue_listeddate,cb_list_annocedate","year="+str(test_date.year))
    fund = pd.DataFrame(fundDate.Data,index = ["zengfa",'peigu','convertible'], columns = fundDate.Codes).T.reset_index()
    filter_limit = pd.to_datetime(test_date_last)
    fund_filtered = fund[(fund["zengfa"] < filter_limit)  & (fund["peigu"] < filter_limit) & (fund["convertible"] < filter_limit)]
    
    #deducted profit/net profit>50%,roe>0.01,currentratio >-1
    other = w.wss(list(fund_filtered["index"]), "deductedprofit,net_profit_is,current,roe,riskadmonition_date","unit=1;rptDate=" + str(test_date.year) + "1231;rptType=1")
    other_pd = pd.DataFrame(other.Data,index = ["deductedprofit",'net_profit','currentratio','roe','riskadmonition_date'], columns = other.Codes).T.reset_index()
    other_pd["net_profit"] = other_pd["net_profit"].astype(float)
    other_pd["deductedprofit"] = other_pd["deductedprofit"].astype(float)
    other_pd["currentratio"] = other_pd["currentratio"].astype(float)
    other_pd["roe"] = other_pd["roe"].astype(float)
    other_pd.eval('NIratio = deductedprofit / abs(net_profit)', inplace = True)
    other_filtered = other_pd.query('NIratio > 0.5 and currentratio > -1 and roe > 0.01')
    other_filtered = other_filtered.rename(columns={"index":"windcode"})
    
    #filter tradevolume,ST
    startdate = (test_date - relativedelta(months=6)).strftime("%Y-%m-%d") 
    enddate = test_date
    tradevolume = w.wss(list(stock_list_i), "avg_amt_per","unit=1;startDate=" + str(startdate).replace("-","") + ";endDate=" + str(enddate).replace("-",""))
    tradevolume_pd = pd.DataFrame(tradevolume.Data,index = ['avg_amt_per'], columns = tradevolume.Codes).T.reset_index().sort_values("avg_amt_per",ascending=False)
    tradevolume_pd = tradevolume_pd.rename(columns={"index":"windcode"})
    t = int(tradevolume_pd.shape[0]*0.9)
    tradevolume_filtered = tradevolume_pd.iloc[:t,:]
    tradevolume_filtered = tradevolume_filtered.merge(stock_list,on='windcode',how='left')
    ST_filtered = tradevolume_filtered[~tradevolume_filtered['name'].str.contains('ST')]
    
    #merge
    basic_pool_list = other_filtered.merge(ST_filtered,on='windcode',how='inner')['windcode']
    
    return basic_pool_list

'''score'''

def get_final_pool(test_date,basic_pool_list):
    """
    
    Parameters
    ----------
    test_date : date
    basic_pool_list : Series

    Returns
    -------
    final_pool_list: Series
        
    """
    
    test_datene1 = test_date+relativedelta(months=-1)
    profit = w.wss(list(basic_pool_list), "pct_chg_per","startDate=" + str(test_datene1).replace("-","") + ";endDate=" + str(test_date).replace("-",""))
    profit_pd = pd.DataFrame(profit.Data,index = ['pct_chg_per'], columns = profit.Codes).T.reset_index().sort_values("pct_chg_per",ascending=False)
    profit_pd['pct_chg_per'] = profit_pd['pct_chg_per'].astype(float)
    profit_pd['scaled'] = profit_pd['pct_chg_per'].apply(lambda x: (x-np.mean(profit_pd['pct_chg_per']))/np.std(profit_pd['pct_chg_per']))
    
    factor = w.wss(list(basic_pool_list), "west_netprofit_FY1,west_netprofit_fy1_3m,pct_chg_per","unit=1;tradeDate=" + str(test_date).replace("-","") +";startDate=" + str(test_datene1).replace("-","") + ";endDate=" + str(test_date).replace("-",""))
    factor_pd = pd.DataFrame(factor.Data,index = ['west_netprofit_FY1','west_netprofit_fy1_3m','pct_chg_per'], columns = factor.Codes).T.reset_index()
    factor_pd['pct_chg_per'] = factor_pd['pct_chg_per'].astype(float)
    factor_pd['pct_scaled'] = factor_pd['pct_chg_per'].apply(lambda x: (x-np.mean(factor_pd['pct_chg_per']))/np.std(factor_pd['pct_chg_per']))
    factor_pd['west_netprofit_FY1'] = factor_pd['west_netprofit_FY1'].astype(float)
    factor_pd['netprofit_FY1_scaled'] = factor_pd['west_netprofit_FY1'].apply(lambda x: (x-np.mean(factor_pd['west_netprofit_FY1']))/np.std(factor_pd['west_netprofit_FY1']))
    factor_pd['west_netprofit_fy1_3m'] = factor_pd['west_netprofit_fy1_3m'].astype(float)
    factor_pd['netprofit_fy1_3m_scaled'] = factor_pd['west_netprofit_fy1_3m'].apply(lambda x: (x-np.mean(factor_pd['west_netprofit_fy1_3m']))/np.std(factor_pd['west_netprofit_fy1_3m']))
    
    factor_scaled = factor_pd.loc[:,['index','pct_scaled','netprofit_FY1_scaled','netprofit_fy1_3m_scaled']].dropna()
    factor_scaled.eval('score = (pct_scaled + netprofit_FY1_scaled + netprofit_fy1_3m_scaled)/3',inplace=True)
    factor_scaled = factor_scaled.sort_values('score',ascending=False)
    f = int(factor_scaled.shape[0]*0.1)
    final_pool_list = factor_scaled['index'][:f]
    
    return final_pool_list


'''Strategy Backtesting'''

po_start = dt.date(2018,5,4) #2018年开始可以
po_end = dt.date(2022,5,4)
change = range(0,po_end.year-po_start.year+1,1)
po_change = [po_start+relativedelta(years=t) for t in change]

trading_days = w.tdays(po_start, po_end, "")

value = 1000000 # initial equity
df_portfolio = pd.DataFrame(trading_days.Data,index=['Time']).T
df_portfolio['Value'] = value
df_portfolio.index = pd.to_datetime(df_portfolio['Time']).dt.date

for i in range(len(po_change)-1):
    test_date = po_change[i]
    test_date_1y = po_change[i+1]
    basic_pool_list = get_basic_pool(test_date)
    final_pool_list = get_final_pool(test_date,basic_pool_list)
    price = w.wsd(list(final_pool_list),'close',test_date,test_date_1y,"PriceAdj=F")
    df_price = pd.DataFrame(price.Data,index=price.Codes,columns=price.Times)
    df_price = df_price.astype(float)
    df_value = df_price.copy()
    df_value.iloc[:,:] = 0
    df_value.iloc[:,0] = value/df_price.shape[0]
    df_position= df_value.iloc[:,0].div(df_price.iloc[:,0],axis=0)
    df_value.iloc[:,1:] = df_price.iloc[:,1:].mul(df_position,axis=0)
    df_value.loc["Value"] = df_value.sum(axis=0)
    df_sum = df_value.iloc[-1,:].reset_index(drop=True)
    df_portfolio.loc[test_date:test_date_1y,"Value"] = list(df_sum)
    value = df_sum.iloc[-1]

df_portfolio['NetValue'] = df_portfolio['Value'].div(df_portfolio.iloc[0,1])


'''Basis'''

basis = "000852.SH" # CSI1000
price_basis = w.wsd(basis,"pct_chg",po_start,po_end,"PriceAdj=F")
df_price_basis = pd.DataFrame(price_basis.Data,index=["pct_chg"],columns=price_basis.Times).T
df_price_basis["pct_chg"] = df_price_basis["pct_chg"]/100
df_price_basis.loc[po_start,'NetValue'] = 1
for j in range(1,df_price_basis.shape[0]):
    df_price_basis.iloc[j,1] = (df_price_basis.iloc[j,0] + 1) * df_price_basis.iloc[j-1,1]


'''plot'''
plt.plot(df_portfolio['Time'],df_portfolio['NetValue'],label='Portfolio')
plt.plot(df_portfolio['Time'],df_price_basis['NetValue'],label='CSI1000')
plt.title("Net Value Trend Comparison")
plt.legend()






