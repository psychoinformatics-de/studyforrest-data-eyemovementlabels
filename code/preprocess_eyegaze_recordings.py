#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import numpy as np
from scipy.signal import savgol_filter # Savitzky–Golay filter, for smoothing data
from scipy.ndimage import median_filter
from scipy import ndimage as ndimage
import os
import os.path as op

import logging
lgr = logging.getLogger('studyforrest.preproc_eyegaze')


def filter_spikes(data):
    """In-place high-frequency spike filter

    Inspired by:

      Stampe, D. M. (1993). Heuristic filtering and reliable calibration
      methods for video-based pupil-tracking systems. Behavior Research
      Methods, Instruments, & Computers, 25(2), 137–142.
      doi:10.3758/bf03204486
    """
    def _filter(arr):
        # over all triples of neighboring samples
        for i in range(1, len(arr) - 1):
            if (arr[i - 1] < arr[i] and arr[i] > arr[i + 1]) \
                    or (arr[i - 1] > arr[i] and arr[i] < arr[i + 1]):
                # immediate sign-reversal of the difference from
                # x-1 -> x -> x+1
                prev_dist = abs(arr[i - 1] - arr[i])
                next_dist = abs(arr[i + 1] - arr[i])
                # replace x by the neighboring value that is closest
                # in value
                arr[i] = arr[i - 1] \
                    if prev_dist < next_dist else arr[i + 1]
        return arr

    data['x'] = _filter(data['x'])
    data['y'] = _filter(data['y'])
    return data


def get_non_nan_clusters(arr):
    clusters, nclusters = ndimage.label(~np.isnan(arr))
    return clusters, nclusters


def get_dilated_nan_mask(arr, iterations, max_ignore_size=None):
    clusters, nclusters = ndimage.label(np.isnan(arr))
    # go through all clusters and remove any cluster that is less
    # the max_ignore_size
    for i in range(nclusters):
        # cluster index is base1
        i = i + 1
        if (clusters == i).sum() <= max_ignore_size:
            clusters[clusters == i] = 0
    # mask to cover all samples with dataloss > `max_ignore_size`
    mask = ndimage.binary_dilation(clusters > 0, iterations=iterations)
    return mask


def preproc(data, px2deg, min_blink_duration=0.02, dilate_nan=0.01,
            median_filter_length=0.05, savgol_length=0.019, savgol_polyord=1,
            sampling_rate=1000.0, max_vel=1000.0):
    """
    Parameters
    ----------
    data : array
      Record array with fields ('x', 'y', 'pupil')
    px2deg : float
      Size of a pixel in visual angles.
    min_blink_duration : float
      In seconds. Any signal loss shorter than this duration with not be
      considered for `dilate_blink`.
    dilate_blink : float
      Duration by which to dilate a blink window (missing data segment) on
      either side (in seconds).
    median_filter_width : float
      Filter window length in seconds.
    savgol_length : float
      Filter window length in seconds.
    savgol_polyord : int
      Filter polynomial order used to fit the samples.
    sampling_rate : float
      In Hertz
    max_vel : float
      Maximum velocity in deg/s. Any velocity value larger than this threshold
      will be replaced by the previous velocity value. Additionally a warning
      will be issued to indicate a potentially inappropriate filter setup.
    """
    # convert params in seconds to #samples
    dilate_nan = int(dilate_nan * sampling_rate)
    min_blink_duration = int(min_blink_duration * sampling_rate)
    savgol_length = int(savgol_length * sampling_rate)
    median_filter_length = int(median_filter_length * sampling_rate)

    # we do not want to change the original data
    data = data.copy()

    data = filter_spikes(data)

    # for signal loss exceeding the minimum blink duration, add additional
    # dilate_nan at either end
    # find clusters of "no data"
    if dilate_nan:
        mask = get_dilated_nan_mask(data['x'], dilate_nan, min_blink_duration)
        data['x'][mask] = np.nan
        data['y'][mask] = np.nan
        data['pupil'][mask] = np.nan

    if savgol_length:
        data['x'] = savgol_filter(data['x'], savgol_length, savgol_polyord)
        data['y'] = savgol_filter(data['y'], savgol_length, savgol_polyord)

    # velocity calculation, exclude velocities over `max_vel`
    # euclidean distance between successive coordinate samples
    # no entry for first datapoint!
    velocities = (np.diff(data['x']) ** 2 + np.diff(data['y']) ** 2) ** 0.5
    # convert from px/sample to deg/s
    velocities *= px2deg * sampling_rate

    med_velocities = np.zeros((len(data),), velocities.dtype)
    med_velocities[1:] = (
        np.diff(median_filter(data['x'], size=median_filter_length)) ** 2 +
        np.diff(median_filter(data['y'], size=median_filter_length)) ** 2) ** 0.5
    # convert from px/sample to deg/s
    med_velocities *= px2deg * sampling_rate
    # remove any velocity bordering NaN
    med_velocities[get_dilated_nan_mask(med_velocities, dilate_nan, 0)] = np.nan

    # replace "too fast" velocities with previous velocity
    # add missing first datapoint
    filtered_velocities = [float(0)]
    for vel in velocities:
        if vel > max_vel:  # deg/s
            # ignore very fast velocities
            lgr.warning(
                'Computed velocity exceeds threshold. '
                'Inappropriate filter setup? [%.1f > %.1f deg/s]',
                vel,
                max_vel)
            vel = filtered_velocities[-1]
        filtered_velocities.append(vel)
    velocities = np.array(filtered_velocities)

    # acceleration is change of velocities over the last time unit
    acceleration = np.zeros(velocities.shape, velocities.dtype)
    acceleration[1:] = (velocities[1:] - velocities[:-1]) * sampling_rate

    return np.core.records.fromarrays([
        med_velocities,
        velocities,
        acceleration,
        # TODO add time np.arange(len(filtered_velocities))
        data['x'],
        data['y']],
        names=['med_vel', 'vel', 'accel', 'x', 'y'])


if __name__ == '__main__':
    px2deg = float(sys.argv[1])
    infpath = sys.argv[2]
    outfpath = sys.argv[3]

    outdir = op.dirname(outfpath)
    outdir = op.curdir if not outdir else outdir
    if not op.exists(outdir):
        os.makedirs(outdir)

    data = np.recfromcsv(
        infpath,
        delimiter='\t',
        names=['x', 'y', 'pupil', 'frame'])

    data = preproc(data, outfpath, px2deg)

    # TODO think about just saving it in binary form
    np.savetxt(
        outfpath,
        data.T,
        fmt=['%f', '%f', '%f', '%f'],
        delimiter='\t')
