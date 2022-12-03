"""
Snowball Options (Float Rebate Monte Carlo)

Description: snowball option pricing with float rebate.

Note: Sensitive information has been obfuscated.

INPUT:
    
s=original price
ko_barrier=knock out price
d_ko=the change to the knock out price, positive is increasing, negative is decreasing
ko_rebate=knock out yield
ki_barrier=knock in price
ehc_kopr=knock out income participation rate
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

OUTPUT:optionvalue

"""
# test params
import numpy as np
s=1.00
ko_barrier=1.00
d_ko=-0.00
ko_rebate_para=np.array([[0.14,0.1],[21,1]])  
ko_rebate=list([])
for i in range(len(ko_rebate_para[0,:])):
    for j in range(int(ko_rebate_para[1,i])):
        ko_rebate=ko_rebate+list([ko_rebate_para[0,i]])
ki_barrier=0.70
ehc_kopr=0
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
    obsv_day_ki=list([tdays]) 

vol=0.20
rf=0.015
q=0.05
futures=False
print (SnowballOptionMC(s,ko_barrier,d_ko,ko_rebate,ki_barrier,ehc_kopr,ki_strike_h,ki_strike_l,tdays,obsv_day_ko,obsv_day_ki,vol,rf,q,futures=True))
#%%
def SnowballOptionMC(s,ko_barrier,d_ko,ko_rebate,ki_barrier,ehc_kopr,ki_strike_h,ki_strike_l,tdays,obsv_day_ko,obsv_day_ki,vol,rf,q,futures=True):
    import numpy as np
    r=(1-futures)*rf
    b=r-q #cost of carry
    nsim=200000
    dt=1/244
    dBt=(dt**0.5)*(np.random.randn(nsim,tdays-1))
    logret=np.exp((b-0.5*vol**2)*dt+vol*dBt)
    logret=np.hstack((np.ones((nsim,1)),logret))
    st=np.cumprod(logret,axis=1)*s

    optionvalue=np.zeros((nsim,1)) #option value
    for i in range(nsim):
        ki_flag=0 #reset
        for j in range(tdays):
            if np.sum(j+1==np.array(obsv_day_ko)) and st[i,j]>=ko_barrier+d_ko*list(obsv_day_ko).index(j+1): 
                optionvalue[i,0]=(ko_rebate[list(obsv_day_ko).index(j+1)]*(j+1)/244+(st[i,j]-1)*ehc_kopr)*(np.exp(-rf*((j+1)/244)))
                break
            elif np.sum(j+1==np.array(obsv_day_ki)) and ki_flag==0 and st[i,j]<ki_barrier: 
                ki_flag=1
            if j==tdays-1 and ki_flag==1: #the last trading day, knock in & not knock out
                optionvalue[i,0]=max(ki_strike_l-1,min(st[i,j]-ki_strike_h,0))*(np.exp(-rf*((j+1)/244)))
            elif j==tdays-1 and ki_flag==0: #the last trading day, not knock in & not knock out
                optionvalue[i,0]=ko_rebate[-1]*(j+1)/244*(np.exp(-rf*((j+12)/244)))
    output_value=np.mean(optionvalue)           
                
    return output_value
