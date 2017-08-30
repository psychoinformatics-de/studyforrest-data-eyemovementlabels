#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import numpy as np
from scipy.signal import savgol_filter # Savitzky–Golay filter, for smoothing data
from glob import glob                  # The glob.glob returns the list of files with their full path
import gzip
import os
from os.path import basename           # returns the tail of the path
from os.path import exists             # logical for if a certain file exists

def preproc(infile, outfile):
    a= gzip.open(infile,"r")
    out=gzip.open(outfile,"wb")
    
    xlist=[]
    ylist=[]
    count=0
    time=[]
    sec=0
    for line in a:
        num=line.split()
        sec+=1
        if num[0]=="0.0":                       # indicates signal, including but not limited to blinks
            count+=1
    
            continue
    
        elif count>20:                          # for signal loss exceeding 20 ms, additional 10 ms at beginning
            for i in range(10):                  # and end are disregarded
                if xlist and ylist and time:
                    xlist.pop()
                    ylist.pop()
                    time.pop()
    
            for i in range(9):
                line=a.readline()
                sec+=1
    
            count=0
            continue
    
        x=float(num[0])
        y=float(num[1])
        xlist.append(x)
        ylist.append(y)
        time.append(sec)
    
    ####### median filter #############
    
    #    for i in range(len(xlist)-8):
    #        xlist[i]=np.mean(xlist[i:i+9])
    #        ylist[i]=np.mean(ylist[i:i+9])
    
    
    ###### savgol filter ##############
    xlist=savgol_filter(xlist,9,1)
    ylist=savgol_filter(ylist,9,1)
    
    
    #velocity calculation, exclude velocities over 1000
    
    vel=[float(0)]
    i=0
    while i<len(xlist)-1:
            d=((xlist[i]-xlist[i+1])**2+(ylist[i]-ylist[i+1])**2)**0.5 #See pg 5 of NYSTROM
            d=d*0.01*1000 #1000 is the sampling rate !(checked=true for both)! and 0.01 is the conversion factor for degrees to pixels. FOR MRI 0.0259930434591
            if d<1000:
                vel.append(d)
            else:
                vel.append(vel[len(vel)-1]) #saves previous value of vel as vel>1000
    
            i+=1
    
    #acceleration calculation
    
    acc=np.diff(vel)/0.001
    acc=np.insert(acc,0,float(0))
    
    #save data to file
    
    data=np.array([vel, acc, time, xlist, ylist])
    data=data.T
    np.savetxt(out, data, fmt=['%.1f', '%.1f', '%d', '%.1f', '%.1f'], delimiter='\t')
    
    out.close()

if __name__ == '__main__':
    subjs = [basename(i) for i in glob('inputs/raw_eyegaze/sub-*')]
    for sub in subjs:
        if not exists(sub):
            os.makedirs(sub)
        for run in range(1, 9):
            print('Doing {} run {}'.format(sub, run))
            run = str(run)
            infile = 'inputs/raw_eyegaze/{sub}/ses-movie/func/{sub}_ses-movie_task-movie_run-{run}_recording-eyegaze_physio.tsv.gz'.format(
                sub=sub,
                run=run)
            if not exists(infile):
                print ('skipping')
                continue
                

            preproc(
                infile,
                '{sub}/eyegaze_run-{run}_preprocessed.tsv.gz'.format(sub=sub, run=run))
