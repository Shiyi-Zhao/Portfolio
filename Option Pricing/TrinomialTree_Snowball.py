"""
Snowball Options (Basic Trinomial Tree)

Description: standard snowball option pricing.

Note: Sensitive information has been obfuscated.

INPUT:

s=original price
ko_barrier=knock out price
ko_jump=jump knock out price（if no jump，equal to ko_barrier）
d_ko=the change to the knock out price, positive is increasing, negative is decreasing
ko_rebate=knock out yield
ki_barrier=knock in price
ki_strike_h=high strike price(knock in)
ki_strike_l=low strike price(knock in)
total_mm=total months(number)
ko_st_mm=observation start month
ki_freq=knock in ovservation frequency（1：day；2：month；3：other,typed in）
tdays=total days（trading days）
obsv_day_ko=knock out observing days（list）
obsv_day_ki=knock in observing days（list）
vol=volatitiy
rf=risk free rate
q=dividend rate
futures=True(futures);False(stock)
is_ki=if knock in
pass_day=holding days

OUTPUT:optionvalue,delta,gamma,theta,prob_ko

"""
# test params
import numpy as np
s=1.00
ko_barrier=1.00
ko_jump=1.00
d_ko=-0.05
ko_rebate=0.23
ki_barrier=0.70
ki_strike_h=1
ki_strike_l=0

total_mm=24
ko_st_mm=3
ki_freq=1  #（1：day；2：month；3：other）
tdays=round(244/12*total_mm)
obsv_day_ko=list(np.rint(np.array(range(ko_st_mm,total_mm+1,1))*244/12))
if ki_freq==1:
    obsv_day_ki=list(np.array(range(1,tdays+1,1)))
elif ki_freq==2:
    obsv_day_ki=list(np.rint(np.array(range(1,total_mm+1,1))*244/12))
else:
    obsv_day_ki=list([tdays])  #enter specialized list

vol=0.20
rf=0.015
q=0.05
futures=False
is_ki=False
pass_day=0a
output=SnowballOptionTriTree(s,ko_barrier,ko_jump,d_ko,ko_rebate,ki_barrier,ki_strike_h,ki_strike_l,tdays,obsv_day_ko,obsv_day_ki,vol,rf,q,futures,is_ki,pass_day)
print (output)
#%%
def SnowballOptionTriTree(s,ko_barrier,ko_jump,d_ko,ko_rebate,ki_barrier,ki_strike_h,ki_strike_l,tdays,obsv_day_ko,obsv_day_ki,vol,rf,q,futures,is_ki,pass_day):
    import numpy as np
    r=(1-futures)*rf
    b=r-q #cost of carry
    if tdays<=300: #steps<1000
        times=2 
    else:
        times=1
    n=tdays*times 
    deltat=tdays/n/244 #244 trading days/year
    u=np.exp(vol*(2*deltat)**0.5)# u and d are forms of volatility
    d=1/u
    pu=((np.exp(b*deltat/2)-np.exp(-vol*(deltat/2)**0.5))/(np.exp(vol*(deltat/2)**0.5)-np.exp(-vol*(deltat/2)**0.5)))**2
    pd=((np.exp(vol*(deltat/2)**0.5)-np.exp(b*deltat/2))/(np.exp(vol*(deltat/2)**0.5)-np.exp(-vol*(deltat/2)**0.5)))**2
    pm=1-pu-pd
    discount_rate=np.exp(-r*deltat) #discount rate
    
    # step 1：price trinomial tree
    pricetree=np.zeros((2*n+1,n+1))
    for j in range(n+1):
        for i in range(2*j+1):
            pricetree[i,j]=s*(u**max(i-j,0))*(d**max(j-i,0))
    
    # step 2：set knock in and knock out roadmap, calculate the probabilities
    ko_true=np.zeros((2*n+1,n+1)) #roadmap:knock out
    ki_true=np.zeros((2*n+1,n+1)) #roadmap:knock in, not knock out
    ki_false=np.zeros((2*n+1,n+1)) #roadmap:not knock in, nor knock out
    for j in range(n+1):
        for i in range(2*j+1):
            if j==0 and not is_ki: #not knock in at the beginning
                ki_false[i,j]=1
                ki_true[i,j]=0
            elif j==0 and is_ki: #knock in at the beginning
                ki_false[i,j]=0
                ki_true[i,j]=1
            else:#corresponding to the trinomial form
                ko_true[i,j]=ko_true[i,j-1]*pd+ko_true[i-1,j-1]*pm+ko_true[i-2,j-1]*pu
                ki_false[i,j]=ki_false[i,j-1]*pd+ki_false[i-1,j-1]*pm+ki_false[i-2,j-1]*pu
                ki_true[i,j]=ki_true[i,j-1]*pd+ki_true[i-1,j-1]*pm+ki_true[i-2,j-1]*pu
            if np.sum(j==np.array(obsv_day_ki)*times) and pricetree[i,j]<ki_barrier and not is_ki: #observing day & knock in
                ki_true[i,j]=ki_true[i,j]+ki_false[i,j]
                ki_false[i,j]=0
            if np.sum(j==np.array(obsv_day_ko)*times) and pricetree[i,j]>=ko_barrier+d_ko*list(obsv_day_ko).index(j/times):  # observing day & knock out
                ko_true[i,j]=ko_true[i,j]+ki_true[i,j]+ki_false[i,j]
                ki_true[i,j]=0
                ki_false[i,j]=0
            elif j==obsv_day_ko[-1]*times and pricetree[i,j]>=ko_jump:  #last observation & jump
                ko_true[i,j]=ko_true[i,j]+ki_true[i,j]+ki_false[i,j]
                ki_true[i,j]=0
                ki_false[i,j]=0
    ki_prob=ki_true/(ko_true+ki_true+ki_false)  
    ko_prob=ko_true/(ko_true+ki_true+ki_false)  
    ko_prob[np.isnan(ko_prob)]=0
    
    # step 3：to expiration date, the value = not_ki_prob*rebate + ki_prob*sell put, then iterate by deltat
    from option_pricing import EuroPVOptionBS,BinaryOption
    optionvalue=np.zeros((2*n+1,n+1))
    for i in range(2*n+1):
        ko_prob_temp=ko_prob[i-1,-2]  #the probability of knock out by last ko_observ
        optionvalue[i,-1]=ko_rebate*(tdays+pass_day)/244*(1-ki_prob[i,-1]-ko_prob_temp)+min(0,pricetree[i,-1]-1)*ki_prob[i,-1]
    ko_time=len(obsv_day_ko)
    for j in range(n):
        if np.sum((n-1-j)==np.array(obsv_day_ko)*times):
            ko_time=ko_time-1
        for i in range((n-1-j)*2+1):
            if np.sum((n-1-j)==np.array(obsv_day_ko)*times) and pricetree[i,n-1-j]>=ko_barrier+d_ko*ko_time: #knock_out observ
                ko_prob_temp=ko_prob[i-1,n-2-j]   
                optionvalue[i,n-1-j]=ko_rebate*((n-1-j)/times+pass_day)/244*(1-ko_prob_temp)  #knock out return
            elif np.sum((n-1-j)==np.array(obsv_day_ki)*times) and pricetree[i,n-1-j]<ki_barrier: #knock in observ+calculate put value by knock in
                optionvalue[i,n-1-j]=-1*(EuroPVOptionBS(pricetree[i,n-1-j],ki_strike_h,((j+1)/times)/244,vol,rf,False,futures)
                                         -EuroPVOptionBS(pricetree[i,n-1-j],ki_strike_l,((j+1)/times)/244,vol,rf,False,futures))*ki_prob[i,n-1-j]
                if ko_jump!=ko_barrier:
                    optionvalue[i,n-1-j]=optionvalue[i,n-1-j]+BinaryOption(pricetree[i,n-1-j],ko_jump,((j+1)/times)/244,vol,rf,ko_rebate*tdays/244,True,False)*np.exp(-r*(n-1-j)/times/244)
            else:  #no knock out, no knock in
                optionvalue[i,n-1-j]=(pu*optionvalue[i+2,n-j]+pm*optionvalue[i+1,n-j]+pd*optionvalue[i,n-j])*discount_rate
    
    from pandas import DataFrame as df
    output=df(np.zeros((1,5)),index=list(['output']),columns=list(['optionvalue','delta','gamma','theta','prob_ko']))
    output.loc['output','optionvalue']=optionvalue[0,0]
    output.loc['output','delta']=(optionvalue[2,1]-optionvalue[0,1])/(s*u-s*d)
    output.loc['output','gamma']=((optionvalue[2,1]-optionvalue[1,1])/(s*u-s)-(optionvalue[1,1]-optionvalue[0,1])/(s-s*d))/(0.5*(s*u-s*d))
    output.loc['output','theta']=(optionvalue[1,1]-optionvalue[0,0])/deltat/365 #trading days 244 or 365
    output.loc['output','prob_ko']=np.sum(ko_true[:,-1])
    
    return output
#%%
output=SnowballOptionTriTree(s,ko_barrier,ko_jump,d_ko,ko_rebate,ki_barrier,ki_strike_h,ki_strike_l,tdays,obsv_day_ko,obsv_day_ki,vol,rf,q,futures,is_ki,pass_day)
print (output)
