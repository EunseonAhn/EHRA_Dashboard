# -*- coding: utf-8 -*-
"""
Created by lmyannie60
2022/02/15
"""

import numpy as np
import pandas as pd
import random
from datetime import datetime,timedelta

filename='August Flow Data.xlsx'

def readcols(filename):
    # read from filename
    dataset1=pd.read_excel(filename)
    fields=[]
    for col in dataset1.columns:
        fields.append(col)
    #print(fields)
    return fields

mu=[53,13,180,14,7,17,37,41,13,26]
total_num=5000

def createdate():
    datelist=np.empty(shape=(total_num,1),dtype=object)
    year,month,day=2022,1,1
    for i in range(total_num):
        datelist[i,0]=str(datetime(year,month,day)+timedelta(hours=i))
    #print(datelist)
    return datelist

def createmonitor():
    monitor_list=np.empty(shape=(total_num,1),dtype=int)
    latitude_list=np.empty(shape=(total_num,1),dtype=float)
    longitude_list=np.empty(shape=(total_num,1),dtype=float)
    for i in range(total_num):
        monitor_list[i,0]=(random.randint(1300,1400)*10)
        latitude_list[i,0]=(random.uniform(0,200))
        longitude_list[i,0]=(random.uniform(0,200))
    return monitor_list,latitude_list,longitude_list

def createsim():
    fields=readcols(filename) # get columns from original data
    mat=np.zeros((total_num,len(mu)))  # store a 0 matrix for all data 2000*?
    monitor_list,latitude_list,longitude_list=createmonitor()
    date_list=createdate() # create 1st column
    for i in range(len(mu)):
        std_dev=random.randint(1,6) # create a scale
        simdata=np.random.normal(mu[i],std_dev,total_num) # create 2000 for i column
        for j in range(total_num):
            mat[j,i]=int(simdata[j])
    final_mat=np.concatenate((date_list,monitor_list,mat,latitude_list,longitude_list),axis=1)
    df=pd.DataFrame(final_mat,columns=fields)
    df.to_excel('simulation.xlsx',sheet_name='sheet1')
    

createsim()