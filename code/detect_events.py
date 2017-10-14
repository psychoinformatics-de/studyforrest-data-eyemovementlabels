#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import numpy as np
from scipy import ndimage
import os
from os.path import join as opj
import sys
import gzip
from os.path import basename
from os.path import exists
from glob import glob

#infile = sys.argv[1]
#outfile = sys.argv[2]

def detect(infile, outfile, fixation_threshold, px2deg):
    data = np.recfromcsv(
        infile,
        delimiter='\t',
        names=['vel', 'accel', 'x', 'y'])
    print ("Data length", len(data))

    out=gzip.open(outfile,"wb")

#####get threshold function #######
    newThr=200                              # What is this "threshold"?
    def getThresh(cut):                     # def refers to defining your own function; cut is input arg
        vel_uthr = data['vel'][data['vel'] < cut]
        avg = vel_uthr.mean()
        sd = vel_uthr.std()
        return avg+6*sd, avg, sd            # outputs of function; average+6*sd denotes a RANGE in any normal distribution

###### threshold function #########      NYSTROM and HOLMQVIST (2010) ALGORITHM IS USED to find a suitable threshold  

    dif=2
    while dif > 1:
        oldThr = newThr                      #Threshold in 100-300 degree/sec. 200 here.
        newThr, avg, sd = getThresh(oldThr)  #Average and std is calculated and Thr is renewed
        dif= abs(oldThr - newThr)           #return absolute value, keep doing the loop until PTn-PTn-1 is smaller than 1 degree

    threshold=newThr
    soft_threshold = avg + 3 * sd
    print("after thr selection", threshold)


####get peaks#### Saccade by definition, is the first velocity that goes below the saccade threshold (NOT VELOCITY threshold)
    peaks=[]

    peaks = np.where(
        np.logical_and(
            data['vel'][:-1] < threshold,
            data['vel'][1:] > threshold))[0]
    # original code had [0] at index 1
    peaks += 1

    above_thr_clusters, nclusters = ndimage.label(data['vel'] > soft_threshold)
    if not nclusters:
        print('Got no above threshold values, baby. Going home...')
        return
    # reinclude any timepoint that has missing data, and treat it as above threshold
    above_thr_clusters[np.isnan(data['vel'])] = 1

    fix=[]
    saccades = []
    for i, pos in enumerate(peaks):
        sacc_start = pos
        while sacc_start > 0 and above_thr_clusters[sacc_start] > 0:
            sacc_start -= 1

        # TODO: make sane
        fix.append(-(sacc_start - 1))  # this is chinese for saying "I am not a fixation"

        off_period_vel = data['vel'][sacc_start - 41:sacc_start]
        # exclude NaN
        off_period_vel = off_period_vel[~np.isnan(off_period_vel)]
        # go with adaptive threshold, but only if the 40ms prior to the saccade have some
        # data to compute a velocity stdev from
        off_threshold = (0.7 * soft_threshold) + \
                        (0.3 * (np.mean(off_period_vel) + 3 * np.std(off_period_vel))) \
                        if len(off_period_vel) > 4 else soft_threshold

        sacc_end = pos
        while sacc_end < len(data) - 1 > 0 and \
                (data['vel'][sacc_end] > off_threshold or \
                 np.isnan(data['vel'][sacc_end])):
            sacc_end += 1
        fix.append(sacc_end)

        # minimum duration 9 ms and no blinks allowed
        if sacc_end - sacc_start > 9 and\
                not np.sum(np.isnan(data['x'][sacc_start:sacc_end])):
            sacc_data = data[sacc_start:sacc_end]
            sacc_data = sacc_data[~np.isnan(sacc_data['vel'])]
            pv = sacc_data['vel'].max()
            amp = (((sacc_data[0]['x'] - sacc_data[-1]['x']) ** 2 + \
                    (sacc_data[0]['y'] - sacc_data[-1]['y']) ** 2) ** 0.5) * px2deg # << WRONG! factor
            avVel = sacc_data['vel'].mean()
            saccades.append((
                sacc_start,
                sacc_end,
                sacc_data[0]['x'],
                sacc_data[0]['y'],
                sacc_data[1]['x'],
                sacc_data[1]['y'],
                amp,
                pv,
                avVel))

######## end of saccade detection = begin of glissade detection ########































#        idx+=1
#        below=False
#        offset=False
#        pval=[]
#        for d in range(40):
#            if idx+d>=len(data)-1: break
#            pval.append(float((data[idx+d])[0]))
#            if float((data[idx+d])[0])<avg+3*sd and float((data[idx+d-1])[0])>avg+3*sd:
#                below=True
#            if below and float((data[idx+d])[0])-float((data[idx+d+1])[0])<=0:
#                ts=float((data[idx+d])[2])
#                xs=float((data[idx+d])[3])
#                ys=float((data[idx+d])[4])
#                offset=True
#        idx=idx+d
#        if offset and len(pval)+11>ts-te+1:      #not more than 10 ms of signal loss in glissades
#            pv=max(pval)
#            amp=(((xs-xe)**2+(ys-ye)**2)**0.5) * px2deg # << WRONG! factor
#            amp= "%.2f" % amp
#            avVel=np.mean(pval)
#            s= " "
#            seq=("GLISS", str(te), str(ts), str(xe), str(ye), str(xs), str(ys), amp, str(pv), str(avVel), '\n')
#            out.write(s.join(seq))
#            fix.pop()
#            fix.append(idx)
#
######### end of glissade detection #######
#
#        if idx>peaks[p]:
#            while p<len(peaks) and idx>=peaks[p]:
#                p+=1
#        else:
#            p+=1
######### fixation detection after everything else is identified ########
#
#    j=0
#
#    while j<len(fix)-1:
#        if fix[j]>0 and abs(fix[j+1])-fix[j]>40:          #onset of fixation
#              ts=float((data[fix[j]])[2])
#              xs=float((data[fix[j]])[3])
#              ys=float((data[fix[j]])[4])
#
#              te=float((data[abs(fix[j+1])])[2])
#              xe=float((data[abs(fix[j+1])])[3])
#              ye=float((data[abs(fix[j+1])])[4])
#
#              pval=[]
#              for i in range(fix[j],abs(fix[j+1])):
#                  pval.append(float((data[i])[0]))
#
#              #pv=max(pval)
#              amp=(((xs-xe)**2+(ys-ye)**2)**0.5)* px2deg # << WRONG! factor
#
#              avVel=np.mean(pval)
#              if avVel<fixation_threshold and amp<2 and len(pval)+11>(te-ts)+1:
#                  amp= "%.2f" % amp
#                  s= " "
#                  seq=("FIX", str(ts), str(te), str(xs), str(ys), str(xe), str(ye), amp, str(avVel), '\n')
#                  out.write(s.join(seq))
#        j+=1
#
#
    # TODO think about just saving it in binary form
    np.savetxt(
        outfile,
        saccades,
        fmt=['%i', '%i', '%f', '%f', '%f', '%f', '%f', '%f', '%f'],
        delimiter='\t')
    print ("done")


if __name__ == '__main__':
    fixation_threshold = float(sys.argv[1])
    px2deg = float(sys.argv[2])
    infpath = sys.argv[3]
    outfpath = sys.argv[4]
    detect(infpath, outfpath, fixation_threshold, px2deg)




#Selection criterion for IVT threshold

#@inproceedings{Olsen:2012:IPV:2168556.2168625,
#author = {Olsen, Anneli and Matos, Ricardo},
#title = {Identifying Parameter Values for an I-VT Fixation Filter Suitable for Handling Data Sampled with Various Sampling Frequencies},
# booktitle = {Proceedings of the Symposium on Eye Tracking Research and Applications},
#series = {ETRA '12},
#year = {2012},
#isbn = {978-1-4503-1221-9},
#location = {Santa Barbara, California},
#pages = {317--320},
#numpages = {4},
#url = {http://doi.acm.org/10.1145/2168556.2168625},
#doi = {10.1145/2168556.2168625},
#acmid = {2168625},
#publisher = {ACM},
#address = {New York, NY, USA},
#keywords = {algorithm, classification, eye movements, scoring},
#} 

#Human-Computer Interaction: Psychonomic Aspects
#edited by Gerrit C. van der Veer, Gijsbertus Mulder
#pg 58-59

#Eye Tracking: A comprehensive guide to methods and measures: Rotting (2001)
#By Kenneth Holmqvist, Marcus Nystrom, Richard Andersson, Richard Dewhurst, Halszka Jarodzka, Joost van de Weijer

#A good reveiw along with a great chunk of the content found in this code:
#@Article{Nystr├Âm2010,
#author="Nystr{\"o}m, Marcus
#and Holmqvist, Kenneth",
#title="An adaptive algorithm for fixation, saccade, and glissade detection in eyetracking data",
#journal="Behavior Research Methods",
#year="2010",
#month="Feb",
#day="01",
#volume="42",
#number="1",
#pages="188--204",
#abstract="Event detection is used to classify recorded gaze points into periods of fixation, saccade, smooth pursuit, blink, and noise. Although there is an overall consensus that current algorithms for event detection have serious flaws and that a de facto standard for event detection does not exist, surprisingly little work has been done to remedy this problem. We suggest a new velocity-based algorithm that takes several of the previously known limitations into account. Most important, the new algorithm identifies so-called glissades, a wobbling movement at the end of many saccades, as a separate class of eye movements. Part of the solution involves designing an adaptive velocity threshold that makes the event detection less sensitive to variations in noise level and the algorithm settings-free for the user. We demonstrate the performance of the new algorithm on eye movements recorded during reading and scene perception and compare it with two of the most commonly used algorithms today. Results show that, unlike the currently used algorithms, fixations, saccades, and glissades are robustly identified by the new algorithm. Using this algorithm, we found that glissades occur in about half of the saccades, during both reading and scene perception, and that they have an average duration close to 24 msec. Due to the high prevalence and long durations of glissades, we argue that researchers must actively choose whether to assign the glissades to saccades or fixations; the choice affects dependent variables such as fixation and saccade duration significantly. Current algorithms do not offer this choice, and their assignments of each glissade are largely arbitrary.",
#issn="1554-3528",
#doi="10.3758/BRM.42.1.188",
#url="https://doi.org/10.3758/BRM.42.1.188"
