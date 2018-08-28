#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import numpy as np
from statsmodels.robust.scale import mad
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
    return amp, pv, avVel


def get_adaptive_saccade_velocity_velthresh(vels, start=300.0):
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
        vel_uthr = vels[vels < cut]
        #avg = np.mean(vel_uthr)
        avg = np.median(vel_uthr)
        #sd = vel_uthr.std()
        sd = mad(vel_uthr)
        return avg + 10 * sd, avg, sd

    # re-compute threshold until value converges
    dif = 2
    while dif > 1:  # less than 1deg/s difference
        old_thresh = cur_thresh
        cur_thresh, avg, sd = _get_thresh(old_thresh)
        lgr.debug(
            'Saccade threshold velocity: %.1f (non-saccade mvel: %.1f, stdvel: %.1f)',
            cur_thresh, avg, sd)
        dif = abs(old_thresh - cur_thresh)

    return cur_thresh, (avg + 5 * sd)


def find_peaks(vels, threshold):
    """Find above-threshold time periods

    Parameters
    ----------
    vels : array
      Velocities.
    threshold : float
      Velocity threshold.

    Returns
    -------
    list
      Each item is a tuple with start and end index of the window where velocities
      exceed the threshold.
    """
    def _get_vels(start, end):
        v = vels[start:end]
        v = v[~np.isnan(v)]
        return v

    sacs = []
    sac_on = None
    for i, v in enumerate(vels):
        if sac_on is None  and v > threshold:
            # start of a saccade
            sac_on = i
        elif sac_on is not None and v < threshold:
            sacs.append((sac_on, i, _get_vels(sac_on, i)))
            sac_on = None
    if sac_on:
        # end of data, but velocities still high
        sacs.append((sac_on, len(vels) - 1, _get_vels(sac_on, len(vels) - 1)))
    return sacs


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


def find_movement_offsetidx(vels, start_idx, off_velthresh):
    idx = start_idx
    # shift saccade end index to the first element that is below the
    # velocity threshold
    while idx < len(vels) - 1 \
            and (vels[idx] > off_velthresh or
                 (vels[idx] > vels[idx + 1])):
            # we used to do this, but it could mean detecting very long
            # saccades that consist of (mostly) missing data
            #    or np.isnan(vels[idx])):
        idx += 1
    return idx


def mk_event_record(data, idx, label, start, end, sampling_rate, px2deg):
    return (
        idx,
        label,
        start / sampling_rate,
        end / sampling_rate,
        data[start]['x'],
        data[start]['y'],
        data[end]['x'],
        data[end]['y']) + \
        get_signal_props(data[start:end], px2deg)


def detect_pso(velocities, sac_velthresh, sac_peak_velthresh):
        pso_peaks = find_peaks(velocities, sac_peak_velthresh)
        if pso_peaks:
            pso_label = 'HVPSO'
        else:
            pso_peaks = find_peaks(velocities, sac_velthresh)
            if pso_peaks:
                pso_label = 'LVPSO'
        if not pso_peaks:
            # no PSO
            return

        # find minimum after the offset of the last reported peak
        pso_end = find_movement_offsetidx(
            velocities, pso_peaks[-1][1], sac_velthresh)

        if pso_end > len(velocities):
            # velocities did not go down within the given window
            return

        return pso_label, pso_end


def detect_saccades(
        data,
        px2deg,
        min_intersaccade_duration=0.1,
        context_window_length=1.0,
        min_saccade_duration=0.01,
        max_saccade_freq=2.0,
        max_pso_duration=0.04,
        sampling_rate=1000.0,
        # RF away
        sort_events=True):

    sac_peak_med_velthresh, sac_onset_med_velthresh = \
        get_adaptive_saccade_velocity_velthresh(data['med_vel'])
    lgr.info('Global saccade MEDIAN velocity thresholds: %.1f, %.1f (onset, peak)',
             sac_onset_med_velthresh, sac_peak_med_velthresh)

    # convert to #samples
    context_window_length = int(context_window_length * sampling_rate)
    min_intersaccade_duration = int(
        min_intersaccade_duration * sampling_rate)
    max_pso_duration = int(max_pso_duration * sampling_rate)
    min_saccade_duration = int(min_saccade_duration * sampling_rate)

    events = []
    saccade_events = []
    saccade_locs = find_peaks(
        data['med_vel'],
        sac_peak_med_velthresh)

    # status map indicating which event class any timepoint has been assigned
    # to so far
    status = np.zeros((len(data),), dtype=int)

    # loop over all peaks sorted by the sum of their velocities
    # i.e. longer and faster goes first
    for i, props in enumerate(sorted(
            saccade_locs, key=lambda x: x[2].sum(), reverse=True)):
        sacc_start, sacc_end, peakvels = props
        lgr.info(
            'Process peak velocity window [%i, %i] at ~%.1f deg/s',
            sacc_start, sacc_end, peakvels.mean())

        # extract velocity data in the vicinity of the peak to calibrate
        # threshold
        win_start = max(
            0,
            sacc_start - int(context_window_length / 2))
        win_end = min(
            len(data),
            sacc_end + context_window_length - (sacc_start - win_start))
        lgr.debug('Actual context window: [%i, %i] -> %i',
                  win_start, win_end, win_end - win_start)

        context_window = data['vel']
        sac_peak_velthresh, sac_onset_velthresh = \
            get_adaptive_saccade_velocity_velthresh(context_window)

        lgr.info('Local saccade velocity thresholds: %.1f, %.1f (onset, peak)',
                 sac_onset_velthresh, sac_peak_velthresh)

        # move backwards in time to find the saccade onset
        sacc_start = find_saccade_onsetidx(
            data['vel'], sacc_start, sac_onset_velthresh)

        # move forward in time to find the saccade offset
        sacc_end = find_movement_offsetidx(
            data['vel'], sacc_end, sac_onset_velthresh)

        sacc_data = data[sacc_start:sacc_end]
        if sacc_end - sacc_start < min_saccade_duration:
            lgr.warn('Skip saccade candidate, too short')
            continue
        elif np.sum(np.isnan(sacc_data['x'])):
            lgr.warn('Skip saccade candidate, missing data')
            continue
        elif status[max(0, sacc_start - min_intersaccade_duration):min(len(data), sacc_end + min_intersaccade_duration)].sum():
            lgr.warn('Skip saccade candidate, too close to another event')
            continue

        event = mk_event_record(
            data, i, "SAC", sacc_start, sacc_end, sampling_rate, px2deg)

        events.append(event)
        saccade_events.append(event)

        # mark as a saccade
        status[sacc_start:sacc_end] = 1

        pso = detect_pso(
            data['vel'][sacc_end:sacc_end + max_pso_duration],
            sac_onset_velthresh,
            sac_peak_velthresh)
        if pso:
            pso_label, pso_end = pso
            psoevent = mk_event_record(
                data, i, pso_label, sacc_end, sacc_end + pso_end,
                sampling_rate, px2deg)
            events.append(psoevent)
            # mark as a saccade part
            status[sacc_end:sacc_end + pso_end] = 1

        if len(saccade_events) / (len(data) / sampling_rate) > max_saccade_freq:
            lgr.info('Stop initial saccade detection, max frequency reached')
            break

    field_names = ['id', 'label', 'start_time', 'end_time', 'start_x', 'start_y',
                   'end_x', 'end_y', 'amp', 'peak_vel', 'avg_vel']

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
