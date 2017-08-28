#!/usr/bin/python
import numpy as np
import os
from os.path import join as opj
import sys
import gzip
from os.path import basename
from os.path import exists
from glob import glob

#infile = sys.argv[1]
#outfile = sys.argv[2]

def preproc(infile, outfile):
    a= gzip.open(infile,"r")
    out=gzip.open(outfile,"wb")

#def proc(infile, outfile):
#    out=open(outfile, "w")

    newThr=200                              # What is this "threshold"?

    data=[]
    with gzip.open(infile, "r") as infileobj:
        for line in infileobj:
            num=line.split()                # Strips away white space
            data.append(num)                # just added all the lines of data (now split) into data []
            
            
            
    print ("Data length", len(data))        

#####get threshold function #######
    def getThresh(cut):                     # def refers to defining your own function; cut is input arg
        temp=[]
        i=0
        while i<len(data):
            if float((data[i])[0])<cut:     #the first [0], which is VELOCITY is checked; if less than 'cut' it is kept. (Thus the cut is an upper boundary for velocity?)
                temp.append(float((data[i])[0]))
            i+=1                            # The value of i is added by 1, thus making a loop going through len(data), ie all the blocks in the array

        avg=np.mean(temp)
        sd=np.std(temp)
        return avg+6*sd, avg, sd            # outputs of function; average+6*sd denotes a RANGE in any normal distribution

###### threshold function #########      NYSTROM and HOLMQVIST (2010) ALGORITHM IS USED to find a suitable threshold  


    avg=0
    sd=0
    dif=2

    while dif>1:
        oldThr=newThr                      #Threshold in 100-300 degree/sec. 200 here.
        newThr, avg, sd=getThresh(oldThr)  #Average and std is calculated and Thr is renewed
        dif=abs(oldThr-newThr)           #return absolute value, keep doing the loop until PTn-PTn-1 is smaller than 1 degree

    threshold=newThr
    print("after thr selection", threshold)


####get peaks#### Saccade by definition, is the first velocity that goes below the saccade threshold
    peaks=[]

    for i in range(len(data)-1):
        if float((data[i])[0])<threshold and float((data[i+1])[0])>threshold:    #for velocities less than threshold and next more than threshold; for FIRST to below threshold, shouldnt this be i-1?
            peaks.append(i+1)                                                    # (contin.) the line number is saved

    p=0
    fix=[]
    while p<len(peaks):
        idx=peaks[p]
        pval=[]
        while float((data[idx])[0])>avg+3*sd and idx!=0:
            pval.append(float((data[idx])[0]))
            idx-=1
        idx+=1
        ts=float((data[idx])[2])                     ###saccade onset
        xs=float((data[idx])[3])
        ys=float((data[idx])[4])
        fix.append(-idx)

        temp=[]
        for i in range (1,41):
            temp.append(float((data[idx-i])[0]))
        offAvg=np.mean(temp)
        offSd=np.std(temp)

        idx=peaks[p]+1
        while idx<len(data) and float((data[idx])[0])>(0.7*(avg+3*sd)+0.3*(offAvg+3+offSd)):
            pval.append(float((data[idx])[0]))
            idx+=1
        idx-=1
        te=float((data[idx])[2])                     ###saccade offset
        xe=float((data[idx])[3])
        ye=float((data[idx])[4])
        fix.append(idx)

        if len(pval)>9 and len(pval)+10>(te-ts+1):      ####minimum duration 9 ms and no blinks allowed
            pv=max(pval)
            amp=(((xs-xe)**2+(ys-ye)**2)**0.5)*0.01
            amp= "%.2f" % amp
            avVel=np.mean(pval)
            s= " "
            seq=("SACC", str(ts), str(te), str(xs), str(ys), str(xe), str(ye), amp, str(pv), str(avVel), '\n')
            out.write(s.join(seq))


####### end of saccade detection = begin of glissade detection ########
        idx+=1
        below=False
        offset=False
        pval=[]
        for d in range(40):
            if idx+d>=len(data)-1: break
            pval.append(float((data[idx+d])[0]))
            if float((data[idx+d])[0])<avg+3*sd and float((data[idx+d-1])[0])>avg+3*sd:
                below=True
            if below and float((data[idx+d])[0])-float((data[idx+d+1])[0])<=0:
                ts=float((data[idx+d])[2])
                xs=float((data[idx+d])[3])
                ys=float((data[idx+d])[4])
                offset=True
        idx=idx+d
        if offset and len(pval)+11>ts-te+1:      #not more than 10 ms of signal loss in glissades
            pv=max(pval)
            amp=(((xs-xe)**2+(ys-ye)**2)**0.5)*0.01
            amp= "%.2f" % amp
            avVel=np.mean(pval)
            s= " "
            seq=("GLISS", str(te), str(ts), str(xe), str(ye), str(xs), str(ys), amp, str(pv), str(avVel), '\n')
            out.write(s.join(seq))
            fix.pop()
            fix.append(idx)

######## end of glissade detection #######

        if idx>peaks[p]:
            while p<len(peaks) and idx>=peaks[p]:
                p+=1
        else:
            p+=1
######## fixation detection after everything else is identified ########

    j=0

    while j<len(fix)-1:
        if fix[j]>0 and abs(fix[j+1])-fix[j]>40:          #onset of fixation
              ts=float((data[fix[j]])[2])
              xs=float((data[fix[j]])[3])
              ys=float((data[fix[j]])[4])

              te=float((data[abs(fix[j+1])])[2])
              xe=float((data[abs(fix[j+1])])[3])
              ye=float((data[abs(fix[j+1])])[4])

              pval=[]
              for i in range(fix[j],abs(fix[j+1])):
                  pval.append(float((data[i])[0]))

              #pv=max(pval)
              amp=(((xs-xe)**2+(ys-ye)**2)**0.5)*0.01

              avVel=np.mean(pval)
              if avVel<6.58 and amp<2 and len(pval)+11>(te-ts)+1:
                  amp= "%.2f" % amp
                  s= " "
                  seq=("FIX", str(ts), str(te), str(xs), str(ys), str(xe), str(ye), amp, str(avVel), '\n')
                  out.write(s.join(seq))
        j+=1


    out.close()
    print ("done")
    
#if __name__ == '__main__':
#    proc(infile, outfile)
    
    
if __name__ == '__main__':
    subjs = [basename(i) for i in glob('sub-*')]
    for sub in subjs:
#        if not exists(sub):
#            os.makedirs(sub)
        for run in range(1, 9):
            print('Doing {} run {}'.format(sub, run))
            run = str(run)
            infile = '{sub}/eyegaze_run-{run}_preprocessed.tsv.gz'.format(
                sub=sub,
                run=run)
#            if not exists(infile):
#                infile = 'inputs/raw_eyegaze/{sub}/beh/{sub}_task-movie_run-{run}_recording-eyegaze_physio.tsv.gz'.format(
#                sub=sub,
#                run=run)

            preproc(
                infile,
                '{sub}/eyegaze_run-{run}_saccades.txt.gz'.format(sub=sub, run=run))

