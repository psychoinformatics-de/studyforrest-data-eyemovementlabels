import numpy as np
from . import utils as ut
from .. import preprocess_eyegaze_recordings as pp
from .. import detect_events as d


common_args = dict(
    px2deg=0.01,
    sampling_rate=1000.0,
)


def test_no_saccade():
    samp = np.random.randn(1001)
    data = ut.expand_samp(samp, y=0.0)
    p = pp.preproc(data, savgol_length=0.0, dilate_nan=0, **common_args)
    # the entire segment is labeled as a fixation
    events = d.detect(p, 50.0, **common_args)
    assert len(events) == 1
    assert events[0]['duration'] == 1.0
    assert events[0]['label'] == 'FIXA'

    # little missing data makes no diff
    p[500:510] = np.nan
    events = d.detect(p, 50.0, **common_args)
    assert len(events) == 1
    assert events[0]['duration'] == 1.0
    assert events[0]['label'] == 'FIXA'

    # but more kills it
    p[500:550] = np.nan
    assert d.detect(p, 50.0, **common_args) is None


def test_one_saccade():
    samp = ut.mk_gaze_sample()

    data = ut.expand_samp(samp, y=0.0)
    nospikes = pp.filter_spikes(data.copy())
    p = pp.preproc(
        nospikes, savgol_length=0.019, savgol_polyord=2,
        dilate_nan=0, **common_args)
    events = d.detect(p, 50.0, **common_args)
    assert events is not None
    # we find at least the saccade
    assert len(events) > 2
    if len(events) == 4:
        # full set
        assert list(events['label']) == ['FIXA', 'SACC', 'LPSO', 'FIXA'] or \
            list(events['label']) == ['FIXA', 'SACC', 'HPSO', 'FIXA']
        for i in range(0, len(events) - 1):
            # complete segmentation
            assert events['start_time'][i + 1] == events['end_time'][i]


def test_too_long_pso():
    samp = ut.mk_gaze_sample(
        pre_fix=1000,
        post_fix=1000,
        sacc=20,
        sacc_dist=200,
        # just under 30deg/s (max smooth pursuit)
        pso=80,
        pso_dist=100)
    data = ut.expand_samp(samp, y=0.0)
    nospikes = pp.filter_spikes(data.copy())
    p = pp.preproc(
        nospikes, savgol_length=0.019, savgol_polyord=2,
        dilate_nan=0, **common_args)
    events = d.detect(p, 50.0, **common_args)
    ut.show_gaze(data, p, events)
    return
    assert events[2]['label'] == 'LPSO'
    # TODO ATM it cannot detect that, figure out whether it should
    assert events[2]['duration'] > 80


def test_real_data():
    data = np.recfromcsv(
        'inputs/raw_eyegaze/sub-09/ses-movie/func/sub-09_ses-movie_task-movie_run-2_recording-eyegaze_physio.tsv.gz',
        #'inputs/raw_eyegaze/sub-02/ses-movie/func/sub-02_ses-movie_task-movie_run-5_recording-eyegaze_physio.tsv.gz',
        delimiter='\t',
        names=['x', 'y', 'pupil', 'frame'])
    #nospikes = pp.filter_spikes(data.copy())
    #from scipy.ndimage import median_filter
    #med_x = median_filter(nospikes['x'], size=100)
    #med_y = median_filter(nospikes['y'], size=100)

    p = pp.preproc(
        data, savgol_length=0.019, savgol_polyord=2,
        dilate_nan=0.01,
        px2deg=0.0185581232561,
        sampling_rate=1000.0,
    )
    clf = d.EyegazeClassifier(
        px2deg=0.0185581232561,
        sampling_rate=1000.0)

    #print(d.get_adaptive_saccade_velocity_velthresh(p, 100))
    events = clf(
        p[:50000],
        #p,
    )

    #print("END")
    #for e in sorted(events, key=lambda x: x['start_time']):
    #    print(e)
    ut.show_gaze(pp=p[:50000], events=events, px2deg=0.0185581232561)
    #ut.show_gaze(pp=p, events=events, px2deg=0.0185581232561)
    #events = None
    import pylab as pl
    #pl.plot(
    #    np.linspace(0, 48000 / 1000.0, 48000),
    #    med_x[:48000])
    #pl.plot(
    #    np.linspace(0, 48000 / 1000.0, 48000),
    #    med_y[:48000])
    #ut.show_gaze(pp=p[:50000], events=events, px2deg=0.0185581232561)
    import pandas as pd
    events = pd.DataFrame(events)
    saccades = events[events['label'] == 'SACC']
    isaccades = events[events['label'] == 'ISAC']
    print('#saccades', len(saccades), len(isaccades))
    pl.plot(saccades['amp'], saccades['peak_vel'], '.', alpha=.3)
    pl.plot(isaccades['amp'], isaccades['peak_vel'], '.', alpha=.3)
    pl.show()


def test_smooth():
    data = np.recfromcsv(
        #'inputs/raw_eyegaze/sub-09/ses-movie/func/sub-09_ses-movie_task-movie_run-2_recording-eyegaze_physio.tsv.gz',
        'inputs/raw_eyegaze/sub-02/ses-movie/func/sub-02_ses-movie_task-movie_run-5_recording-eyegaze_physio.tsv.gz',
        delimiter='\t',
        names=['x', 'y', 'pupil', 'frame'])
    #nospikes = pp.filter_spikes(data.copy())
    #from scipy.ndimage import median_filter
    #med_x = median_filter(nospikes['x'], size=100)
    #med_y = median_filter(nospikes['y'], size=100)

    p = pp.preproc(
        data[:50000],
        savgol_length=0.019, savgol_polyord=2,
        dilate_nan=0.01,
        px2deg=0.0185581232561,
        sampling_rate=1000.0,
    )

    #trial = p[9588:9844]
    trial = p[34859:35690]

    f = data[:len(trial)]
    f[:] = np.nan

    from scipy import signal

    def _butter_lowpass(cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    b, a = _butter_lowpass(20.0, 1000.0)
    f['x'] = signal.filtfilt(b, a, trial['x'], method='gust')
    f['y'] = signal.filtfilt(b, a, trial['y'], method='gust')

    ut.show_gaze(data=f, pp=trial, events=None, px2deg=0.0185581232561)
