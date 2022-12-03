# -*- coding: utf-8 -*-
"""

Description: process raw data and extract specific placement info.

Note: Sensitive information has been obfuscated.

"""

'''import and set keyword'''
import os
import pandas as pd
keruiSeries = ["ProductNameA","ProductNameB","ProductNameC"]
henruiSeries = ["ProductNameX","ProductNameY","ProductNameZ"]
nameInput = keruiSeries
path = "Path"
name = [str(fname) for fname in os.listdir(path) if ".xlsx" in fname and "placement" not in fname] #import stock name
if nameInput == keruiSeries:
    sheets=["NameA","NameB","NameC"]
elif nameInput == henruiSeries:
    sheets=["NameX","NameY","NameZ"]

'''Data extration'''
transfer=pd.DataFrame([nameInput,sheets]).transpose()
transfer=transfer.rename(columns={0:'Investor',1:'SheetName'})
total_output = pd.DataFrame()
for i in range(len(name)):
    excel = pd.read_excel(path+name[i])
    new_excel = excel.iloc[:,[3,8]]
    new_excel.columns = ['Investor','Placement']
    
    output = pd.DataFrame(columns=['Investor','Placement','StockName'])
    for nameInput_i in nameInput:
        output=output.append(new_excel[new_excel.Investor == nameInput_i])
    output.iloc[:,-1]=name[i][:-5]
    total_output=total_output.append(output)
    print(name[i])

''' data processing and export'''
total_output=total_output.sort_values(by='Investor')
total_output=total_output.merge(transfer,how='left',on='Investor')
total_output=total_output.loc[:,['Investor','SheetName','StockName','Placement']]
total_output.insert(3,'Find',total_output['SheetName']+total_output['StockName'])
total=total_output.groupby(by=['Investor','SheetName','StockName','Find']).sum().reset_index()
total.to_excel(path + sheets[0] +".xlsx")















