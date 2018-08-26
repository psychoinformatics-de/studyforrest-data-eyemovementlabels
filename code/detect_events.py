#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import numpy as np
from scipy import ndimage
import sys
import gzip

import logging
lgr = logging.getLogger('studyforrest.detect_eyegaze_events')


def get_signal_props(data, px2deg):
    data = data[~np.isnan(data['vel'])]
    pv = data['vel'].max()
    amp = (((data[0]['x'] - data[-1]['x']) ** 2 + \
            (data[0]['y'] - data[-1]['y']) ** 2) ** 0.5) * px2deg
    avVel = data['vel'].mean()
    return pv, amp, avVel


def get_adaptive_saccade_velocity_velthresh(data, start=300.0):
    """Determine saccade peak velocity threshold.

    Takes global noise-level of data into account. Implementation
    based on algorithm proposed by NYSTROM and HOLMQVIST (2010).

    Parameters
    ----------
    start : float
      Start velocity for adaptation algorithm. Should be larger than
      any conceivable minimal saccade velocity (in deg/s).
    TODO std unit multipliers

    Returns
    -------
    tuple
      (peak saccade velocity threshold, saccade onset velocity threshold). The latter
      (and lower) value can be used to determine a more precise saccade onset.
    """
    cur_thresh = start

    def _get_thresh(cut):
        # helper function
        vel_uthr = data['vel'][data['vel'] < cut]
        avg = vel_uthr.mean()
        sd = vel_uthr.std()
        return avg + 6 * sd, avg, sd

    # re-compute threshold until value converges
    dif = 2
    while dif > 1:  # less than 1deg/s difference
        old_thresh = cur_thresh
        cur_thresh, avg, sd = _get_thresh(old_thresh)
        lgr.info(
            'Saccade threshold velocity: %.1f (non-saccade mvel: %.1f, stdvel: %.1f)',
            cur_thresh, avg, sd)
        dif = abs(old_thresh - cur_thresh)

    return cur_thresh, (avg + 3 * sd)


def find_saccades(vels, threshold):
    """Find time periods with saccades

    Parameters
    ----------
    vels : array
      Velocities.
    threshold : float
      Velocity threshold to identify a saccade.

    Returns
    -------
    list
      Each item is a tuple with start and end index of the window where velocities
      exceed the threshold.
    """
    sacs = []
    sac_on = None
    for i, v in enumerate(vels):
        if sac_on is None  and v > threshold:
            # start of a saccade
            sac_on = i
        elif sac_on and v < threshold:
            sacs.append((sac_on, i))
            sac_on = None
    if sac_on:
        # end of data, but velocities still high
        sacs.append((sac_on, len(vels) - 1))

    if not len(sacs):
        lgr.warn('Got no above saccade peak threshold velocity values')
    return sacs


def get_saccade_end_velthresh(vels, start_idx, width, sac_onset_velthresh):
    off_period_vel = vels[max(0, start_idx - width - 1):start_idx]
    # exclude NaN
    off_period_vel = off_period_vel[~np.isnan(off_period_vel)]
    # go with adaptive threshold, but only if the window prior to the
    # saccade have some data to compute a velocity stdev from
    off_velthresh = \
        (0.7 * sac_onset_velthresh) + \
        (0.3 * (np.mean(off_period_vel) + 3 * np.std(off_period_vel))) \
        if len(off_period_vel) > width else sac_onset_velthresh
    return off_velthresh


def find_saccade_onsetidx(vels, start_idx, sac_onset_velthresh):
    idx = start_idx
    while idx > 0 \
            and (vels[idx] > sac_onset_velthresh or
                 vels[idx] <= vels[idx - 1]):
        # find first local minimum after vel drops below onset threshold
        # going backwards in time

        # we used to do this, but it could mean detecting very long
        # saccades that consist of (mostly) missing data
        #         or np.isnan(vels[sacc_start])):
        idx -= 1
    return idx


def find_saccade_offsetidx(vels, start_idx, onset_idx, sac_onset_velthresh,
                           minimum_fixation_duration):
    # determine velocity threshold for the saccade end, based on
    # velocity stdev immediately prior the saccade start
    off_velthresh = get_saccade_end_velthresh(
        vels,
        onset_idx,
        minimum_fixation_duration,
        sac_onset_velthresh)
    lgr.debug(
        'Adaptive saccade offset velocity threshold '
        '%.1f (vs onset threshold %.1f)',
        off_velthresh, sac_onset_velthresh)

    idx = start_idx
    # shift saccade end index to the first element that is below the
    # velocity threshold
    while idx < len(vels) - 1 > 0 \
            and (vels[idx] > off_velthresh or
                 (vels[idx] > vels[idx + 1])):
            # we used to do this, but it could mean detecting very long
            # saccades that consist of (mostly) missing data
            #    or np.isnan(vels[idx])):
        idx += 1
    return idx


def detect(data,
           fixation_velthresh,
           px2deg,
           minimum_fixation_duration=0.04,
           sampling_rate=1000.0,
           sort_events=True):
    # find velocity thresholds for saccade detection
    sac_peak_velthresh, sac_onset_velthresh = \
        get_adaptive_saccade_velocity_velthresh(data)
    lgr.info('Global saccade velocity thresholds: %.1f, %.1f (onset, peak)',
             sac_onset_velthresh, sac_peak_velthresh)

    # comvert to #samples
    minimum_fixation_duration = int(minimum_fixation_duration * sampling_rate)

    events = []
    saccade_locs = []
    fix=[]

    velocities = data['vel']

    saccade_locs = find_saccades(
        velocities,
        sac_peak_velthresh)

    for i, pos in enumerate(saccade_locs):
        sacc_start, sacc_end = pos
        if fix and sacc_end < fix[-1]:
            lgr.debug(
                'Skipping saccade peak velocity window [%i, %i], '
                'inside prev. reported saccade/PSO window (ends at %i)',
                sacc_start, sacc_end, fix[-1])
            continue
        lgr.debug('Investigation above saccade peak threshold velocity window [%i, %i]',
                  sacc_start, sacc_end)

        sacc_start = find_saccade_onsetidx(
            velocities, sacc_start, sac_onset_velthresh)

        if not fix:
            # start with a fixation
            lgr.debug('No fixation candidate start yet, appending')
            fix.append(0)
        # this is sophisticated for saying "I am not a fixation anymore"
        fix.append(-sacc_start)
        lgr.debug('Fixation candidate end/saccade start at %i', abs(fix[-1]))

        sacc_end = find_saccade_offsetidx(
            velocities, sacc_end, sacc_start, sac_onset_velthresh,
            minimum_fixation_duration)

        # mark start of a fixation
        fix.append(sacc_end)
        lgr.debug('Saccade end/fixation candidate start at %i', abs(fix[-1]))

        # minimum duration 9 ms and no blinks allowed
        # second test should be redundant, but we leave it, because the cost
        # is low
        if sacc_end - sacc_start >= 9 and\
                not np.sum(np.isnan(data['x'][sacc_start:sacc_end])):
            sacc_data = data[sacc_start:sacc_end]
            pv, amp, avVel = get_signal_props(sacc_data, px2deg)
            sacc_duration = sacc_end - sacc_start
            events.append((
                "SAC",
                sacc_start / sampling_rate,
                sacc_end / sampling_rate,
                sacc_data[0]['x'],
                sacc_data[0]['y'],
                sacc_data[-1]['x'],
                sacc_data[-1]['y'],
                amp,
                pv,
                avVel,
                sacc_duration))

        gldata = data[sacc_end:sacc_end + minimum_fixation_duration]
        # going from the end of the window to find the last match
        for i in range(0, len(gldata) - 2):
            # velocity after saccade end goes below the saccade onset threshold
            # and immediately afterwards stay or increases the velocity again
            if gldata[(-1 * i) - 2]['vel'] < sac_onset_velthresh and \
                    gldata[(-1 * i) - 1]['vel'] > sac_onset_velthresh and \
                    gldata[(-1 * i) -3]['vel'] >= gldata[(-1 * i) -2]['vel']:
                gliss_data = gldata[:-i]
                gliss_end = sacc_end + len(gldata) - i

                if not len(gliss_data) or \
                        np.sum(np.isnan(gliss_data['vel'])) > 10:
                    # not more than 10 ms of signal loss in post saccadic
                    # oscilations/glissades
                    break
                pv, amp, avVel = get_signal_props(gliss_data, px2deg)
                gl_duration = gliss_end - (sacc_end + 1)
                events.append((
                    "PSO",
                    sacc_end / sampling_rate,
                    gliss_end / sampling_rate,
                    gldata[0]['x'],
                    gldata[0]['y'],
                    gldata[-i]['x'],
                    gldata[-1]['y'],
                    amp,
                    pv,
                    avVel,
                    gl_duration))
                fix.pop()
                fix.append(gliss_end)
                lgr.debug('PSO found, moved fixation candidate start to %i', abs(fix[-1]))
                break

######### fixation detection after everything else is identified ########
    # currently completely ignored
    if not fix:
        # we got nothing whatsoever, the whole thing is a fixation
        fix.append(0)
        lgr.debug('No fixation candidate start yet, appending')
    if not fix[-1] < 0:
        # end of fixation it missing
        fix.append(-(len(data) - 1))
        lgr.debug('Closing final fixation candidate at %i', abs(fix[-1]))

    for j, f in enumerate(fix[:-1]):
        if f < 0:
            # fixation end time, skip
            continue
        fix_start = f
        # end times are coded negative
        fix_end = abs(fix[j + 1])
        if fix_start >= 0 and fix_end - f > minimum_fixation_duration:
            fixdata = data[fix_start:fix_end]
            if not len(fixdata) or np.isnan(fixdata[0][0]):
                lgr.error("Erroneous fixation interval")
                continue
            pv, amp, avVel = get_signal_props(fixdata, px2deg)
            fix_duration = fix_end - fix_start

            # TODO if there is too much data loss, split fixation in multiple parts
            if avVel < fixation_velthresh and amp < 2 and np.sum(np.isnan(fixdata['vel'])) <= 10:
                events.append((
                    "FIX",
                    fix_start / sampling_rate,
                    abs(fix[j + 1]) / sampling_rate,
                    data[fix_start]['x'],
                    data[fix_start]['y'],
                    data[fix_end]['x'],
                    data[fix_end]['y'],
                    amp,
                    pv,
                    avVel,
                    fix_duration / sampling_rate))

    field_names = ['label', 'start_time', 'end_time', 'start_x', 'start_y',
                   'end_x', 'end_y', 'dist', 'peak_vel', 'avg_vel', 'duration']
    events = np.core.records.fromrecords(
        events,
        names=field_names,
    ) if events else None

    if events is not None and sort_events:
        events.sort(order='start_time')
        return events
    else:
        return events


if __name__ == '__main__':
    fixation_velthresh = float(sys.argv[1])
    px2deg = float(sys.argv[2])
    infpath = sys.argv[3]
    outfpath = sys.argv[4]
    data = np.recfromcsv(
        infpath,
        delimiter='\t',
        names=['vel', 'accel', 'x', 'y'])

    events = detect(data, outfpath, fixation_velthresh, px2deg)

    # TODO think about just saving it in binary form
    f = gzip.open(outfpath, "w")
    for e in events:
        f.write('%s\t%i\t%i\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\n' % e)
    print ("done")






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
