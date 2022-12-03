# -*- coding: utf-8 -*-
"""
Snowball Options (Basic Monte Carlo)

Description: simulate income distribution of snowball option by Monte Carlo Methods.

Note: Sensitive information has been obfuscated.

INPUT:
    
s=original price
ko=knock out price
d_ko=the change to the knock out price, positive is increasing, negative is decreasing
ko_rebate=knock out yield
ki_barrier=knock in price
ki_strick=strike price
tdays=total days（trading days）
obsv_day=observation day(list)
vol=volatitiy
rf=risk free rate
q=dividend rate
futures=True(futures);False(stock)

OUTPUT:optionvalue

"""
# test params
s=1
ko_barrier=1.00
d_ko=-0.005
ko_rebate=0.23
ki_barrier=0.70
ki_strike=1
tdays=488
obsv_day=list([62,82,103,123,143,164,184,204,224,244,265,285,305,326,346,367,387,407,428,448,468,488])
vol=0.1862
rf=0.02
q=0.02
futures=False

#%%
def SnowballOptionMC(s,ko_barrier,d_ko,ko_rebate,ki_barrier,ki_strike,tdays,obsv_day,vol,rf,q,futures=True):
    import numpy as np
    r=(1-futures)*rf
    b=r-q #cost of carry
    nsim=200000
    dt=1/244
    dBt=(dt**0.5)*(np.random.randn(nsim,tdays-1)) #norm
    logret=np.exp((b-0.5*vol**2)*dt+vol*dBt)
    logret=np.hstack((np.ones((nsim,1)),logret))
    st=np.cumprod(logret,axis=1)*s

    optionvalue=np.zeros((nsim,1))
    for i in range(nsim):
        ki_flag=0 #reset knock in flag
        for j in range(tdays-1):
            if np.sum(j+2==np.array(obsv_day)) and st[i,j+1]>=ko_barrier+d_ko*list(obsv_day).index(j+2):
                optionvalue[i,0]=ko_rebate*(j+2)/244*(np.exp(-rf*((j+2)/244)))  #return
                break
            elif ki_flag==0 and st[i,j+1]<ki_barrier: #if knock in
                ki_flag=1
            if j==tdays-2 and ki_flag==1: #the last trading day, knock in & not knock out
                optionvalue[i,0]=min(st[i,j+1]-ki_strike,0)*(np.exp(-rf*((j+2)/244)))
            elif j==tdays-2 and ki_flag==0: #the last trading day, not knock in & not knock out
                optionvalue[i,0]=ko_rebate*(j+2)/244*(np.exp(-rf*((j+2)/244)))
    output_value=np.mean(optionvalue)           
                
    return output_value
#%%
SnowballOptionMC(s,ko_barrier,d_ko,ko_rebate,ki_barrier,ki_strike,tdays,obsv_day,vol,rf,q,futures)