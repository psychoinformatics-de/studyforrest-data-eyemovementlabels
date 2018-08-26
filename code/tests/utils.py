import numpy as np
import os

import logging
lgr = logging.getLogger('studyforrest.utils')


if 'NOISE_SEED' in os.environ:
    seed = int(os.environ['NOISE_SEED'])
else:
    seed = np.random.randint(100000000)
    lgr.warn('RANDOM SEED: %i', seed)
np.random.seed(seed)


def get_noise(size, loc, std):
    noise = np.random.randn(size)
    noise *= std
    noise += loc
    return noise


def get_drift(size, start, dist):
    return np.linspace(start, start + dist, size)


def mk_gaze_sample(
        pre_fix=1000,
        post_fix=1000,
        fix_std=5,
        sacc=20,
        sacc_dist=200,
        glis=30,
        glis_dist=-40,
        start_x=0.0,
        noise_std=2,
        ):
    duration = pre_fix + sacc + glis + post_fix
    samp = np.empty(duration)
    # pre_fix
    t = 0
    pos = start_x
    samp[t:t + pre_fix] = get_noise(pre_fix, pos, fix_std)
    t += pre_fix
    # saccade
    samp[t:t + sacc] = get_drift(sacc, pos, sacc_dist)
    t += sacc
    pos += sacc_dist
    # glissade
    samp[t:t + glis] = get_drift(glis, pos, glis_dist)
    t += glis
    pos += glis_dist
    # post fixation
    samp[t:t + post_fix] = get_noise(post_fix, pos, fix_std)
    samp += get_noise(len(samp), 0, noise_std)

    return samp


def expand_samp(samp, y=1000.0):
    n = len(samp)
    return np.core.records.fromarrays([
        samp,
        [y] * n,
        [0.0] * n,
        [0] * n],
        names=['x', 'y', 'pupil', 'frame'])


def samp2file(data, fname):
    np.savetxt(
        fname,
        data.T,
        fmt=['%.1f', '%.1f', '%.1f', '%i'],
        delimiter='\t')


def show_gaze(data=None, pp=None, events=None, sampling_rate=1000.0):
    colors = {
        'FIX': 'gray',
        'SAC': 'green',
        'PSO': 'yellow',
    }

    import pylab as pl
    if data is not None:
        pl.plot(
            np.linspace(0, len(data) / sampling_rate, len(data)),
            data['x'],
            color='blue')
    if pp is not None:
        pl.plot(
            np.linspace(0, len(pp) / sampling_rate, len(pp)),
            pp['x'],
            color='orange')
    if events is not None:
        for ev in events:
            pl.axvspan(
                ev['start_time'],
                ev['end_time'],
                color=colors[ev['label']],
                alpha=0.3)
    pl.show()
