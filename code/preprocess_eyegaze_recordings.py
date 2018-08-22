#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import sys
import numpy as np
from scipy.signal import savgol_filter # Savitzky–Golay filter, for smoothing data
from scipy import ndimage as ndimage
from glob import glob                  # The glob.glob returns the list of files with their full path
import gzip
import os
from os.path import basename           # returns the tail of the path
from os.path import dirname
from os.path import curdir
from os.path import exists             # logical for if a certain file exists
from os.path import join as opj

sampling_rate = 1000.0  # in Hertz


def preproc(infile, outfile, px2deg):
    # TODO parameter
    # max_signal_loss_without_something
    # blank_duration
    # savgol_window_length
    # savgol_polyord
    # savgol_iterations

    outdir = dirname(outfile)
    outdir = curdir if not outdir else outdir
    if not exists(outdir):
        os.makedirs(outdir)

    data = np.recfromcsv(
        infile,
        delimiter='\t',
        names=['x', 'y', 'pupil', 'frame'])

    # for signal loss exceeding 20 ms, additional 10 ms at beginning
    # find clusters of "no data"
    clusters, nclusters = ndimage.label(np.isnan(data['x']))
    # go through all clusters and remove any cluster that is less than 20 samples
    for i in range(1, nclusters):
        if (clusters == i).sum() <= 20:
            clusters[clusters == i] = 0
    # mask to cover all samples with dataloss > 20ms, plus 10 samples on either
    # side of the lost segment
    mask = ndimage.binary_dilation(clusters > 0, iterations=10)
    data['x'][mask] = np.nan
    data['y'][mask] = np.nan
    data['pupil'][mask] = np.nan

    # TODO filtering with NaNs in place kicks out additional datapoints, maybe
    # do no or less dilation of the mask above
    data['x'] = savgol_filter(data['x'], 19, 1)
    data['y'] = savgol_filter(data['y'], 19, 1)

    #velocity calculation, exclude velocities over 1000

    # euclidean distance between successive coordinate samples
    # no entry for first datapoint
    velocities = (np.diff(data['x']) ** 2 + np.diff(data['y']) ** 2) ** 0.5

    # convert from px/msec to deg/s
    velocities *= px2deg * sampling_rate

    # replace "too fast" velocities with previous velocity
    accelerations = [float(0)]
    filtered_velocities = [float(0)]
    for vel in velocities:
        # TODO make threshold a parameter
        if vel > 1000:  # deg/s
            # ignore very fast velocities
            vel = filtered_velocities[-1]
        # acceleration is change of velocities over the last msec
        accelerations.append((vel - filtered_velocities[-1]) * sampling_rate)
        filtered_velocities.append(vel)
    # TODO report how often that happens

    #save data to file
    data=np.array([
        filtered_velocities,
        accelerations,
        # TODO add time np.arange(len(filtered_velocities))
        data['x'],
        data['y']])

    # TODO think about just saving it in binary form
    np.savetxt(
        outfile,
        data.T,
        fmt=['%f', '%f', '%f', '%f'],
        delimiter='\t')

if __name__ == '__main__':
    px2deg = float(sys.argv[1])
    infpath = sys.argv[2]
    outfpath = sys.argv[3]
    preproc(infpath, outfpath, px2deg)
