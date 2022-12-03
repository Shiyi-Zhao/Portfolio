"""
Volatility Get

Description: calculate 1/3/6/12/24/Garch volatiities.

Note: Sensitive information has been obfuscated.

INPUT:
    
codes=list(codes)  code:stock or stock index, contract code: futures
date=dt.date(year,month,day)/dt.date.today()

OUTPUT:garch volatility，1M、3M、6M、12M、24M volatility and percentiles

"""

#test params
from WindPy import *
w.start()
import datetime as dt
codes=list(['AU.SHF','SC.INE','CU.SHF'])
#codes=list(['HSI.HI','HSCEI.HI','HSTECH.HI'])
#codes=list(['000300.SH','IF.CFE','000905.SH','IC.CFE','000016.SH','000825.SH'])
date=dt.date.today() #dt.date(year,month,day)/dt.date.today()

#%%
def VolatilityGet(codes,date):
    import datetime as dt
    import numpy as np
    from arch import arch_model
    import pandas as pd
    from pandas import DataFrame as df
    import talib

    lastworkingday=w.tdaysoffset(-1, dt.date.today(), "").Data[0][0]
    vol_list=list(['garch','1M_vol','1M_pct','3M_vol','3M_pct','6M_vol','6M_pct','12M_vol','12M_pct','24M_vol','24M_pct'])
    output=df(np.zeros((len(codes),len(vol_list))),index=codes,columns=vol_list)
    pct=np.array([1,10,25,50,75,90,99])
    tenor=np.array([1,3,6,12,24,36])
    vol_cones=np.zeros((len(codes),len(tenor),len(pct)))
    vol_lastmonth=df(np.zeros((len(codes),5)),index=codes,columns=list(['1M_vol','3M_vol','6M_vol','12M_vol','24M_vol']))
    
    for i in range(len(codes)):
        #i = 0
        startdate=w.wss(codes[i], "contract_issuedate,launchdate,ipo_date").Data
        if startdate[0]>startdate[1]: # if True, futures; if False, stocks or stock indexes
            startdate.append([dt.datetime(2010,1,1,0,0)])
            startdate=max(startdate)
            hisinfo=w.wsd(codes[i], "trade_hiscode", startdate[0], lastworkingday, "Fill=Previous")
            hiscode=hisinfo.Data[0] #historical main contract code
            histime=hisinfo.Times
            index=np.array([temp for temp,a in enumerate(np.array(hiscode[:-1])!=np.array(hiscode[1:])) if a==True])
            index=np.hstack([0,index,len(histime)-1])
            ret=np.zeros((len(histime)))
            for j in range(len(index)-1):
                #j=0
                ret[(index[j]+1):(index[j+1]+1)]=w.wsd(hiscode[index[j]+1], "pctchange_close", histime[index[j]+1], histime[index[j+1]], "").Data[0]
        else:
            startdate=startdate[-1]
            ret=np.array(w.wsd(codes[i], "pct_chg", startdate[0], lastworkingday, "").Data[0])
        ret = ret[~np.isnan(ret)]
                
        """Eliminate Extreme Values"""
        # per_u=np.percentile(ret,99)
        # per_d=np.percentile(ret,1)
        # ret[(ret>per_u)]=per_u
        # ret[(ret<per_d)]=per_d
        """garch"""
        garch11 = arch_model(ret, mean='Zero', p=1, q=1)
        result = garch11.fit(update_freq=0)
        period=122 #6M garch prediction
        output.loc[codes[i],'garch']=np.sqrt(np.sum(result.forecast(horizon=period).variance.iloc[-1])*(244/period))/100 #,method='bootstrap'z
        """hist vol"""
        ret=ret/100
        vol_1M=talib.STDDEV(ret,timeperiod=20)*np.sqrt(244*20/19)
        vol_3M=talib.STDDEV(ret,timeperiod=61)*np.sqrt(244*61/60)
        vol_6M=talib.STDDEV(ret,timeperiod=122)*np.sqrt(244*122/121)
        vol_12M=talib.STDDEV(ret,timeperiod=244)*np.sqrt(244*244/243)
        vol_24M=talib.STDDEV(ret,timeperiod=488)*np.sqrt(244*488/487)
        vol_36M=talib.STDDEV(ret,timeperiod=732)*np.sqrt(244*732/731)
        output.loc[codes[i],'1M_vol']=vol_1M[-1]
        output.loc[codes[i],'3M_vol']=vol_3M[-1]
        output.loc[codes[i],'6M_vol']=vol_6M[-1]
        output.loc[codes[i],'12M_vol']=vol_12M[-1]
        output.loc[codes[i],'24M_vol']=vol_24M[-1]
        vol_lastmonth.loc[codes[i],'1M_vol']=vol_1M[-23]
        vol_lastmonth.loc[codes[i],'3M_vol']=vol_3M[-23]
        vol_lastmonth.loc[codes[i],'6M_vol']=vol_6M[-23]
        vol_lastmonth.loc[codes[i],'12M_vol']=vol_12M[-23]
        vol_lastmonth.loc[codes[i],'24M_vol']=vol_24M[-23]
        output.loc[codes[i],'1M_pct']=np.nansum(vol_1M<vol_1M[-1])/(len(ret)-20)
        output.loc[codes[i],'3M_pct']=np.nansum(vol_3M<vol_3M[-1])/(len(ret)-61)
        output.loc[codes[i],'6M_pct']=np.nansum(vol_6M<vol_6M[-1])/(len(ret)-122)
        output.loc[codes[i],'12M_pct']=np.nansum(vol_12M<vol_12M[-1])/(len(ret)-244)
        output.loc[codes[i],'24M_pct']=np.nansum(vol_24M<vol_24M[-1])/(len(ret)-488)
        """Volatility Cones"""
        vol_temp=np.vstack([vol_1M,vol_3M,vol_6M,vol_12M,vol_24M,vol_36M]).T
        for t in range(len(tenor)):
            for p in range(len(pct)):
                vol_cones[i,t,p]=np.nanpercentile(vol_temp[:,t],pct[p])

    return output, vol_cones,vol_lastmonth
#%%
[vol_output,volcones_output,vol_lastmonth]=VolatilityGet(codes,date)
#%%
code='000905.SH' #plot

import numpy as np
import matplotlib.pyplot as plt
label_list=list(['1%percentile','10%percentile','25%percentile','50%percentile','75%percentile','90%percentile','99%percentile'])
tenor=list([1,3,6,12,24,36])
codeindex=codes.index(code)
for i in range(len(label_list)):
    plt.plot(tenor,volcones_output[codeindex,:,i],label=label_list[i])
plt.plot(tenor[:-1],np.array(vol_output.loc[code,list(['1M_vol','3M_vol','6M_vol','12M_vol','24M_vol'])]),'rs',label='current vol')
plt.plot(tenor[:-1],np.array(vol_lastmonth.loc[code,:]),'g^',label='last month vol')

plt.xlabel('month')
plt.ylabel('volatility')
plt.title(code)
plt.legend(fontsize=7,loc=1)
plt.show()
    