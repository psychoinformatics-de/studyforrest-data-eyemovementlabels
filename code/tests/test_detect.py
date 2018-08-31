import numpy as np
from . import utils as ut
from .. import detect_events as d


common_args = dict(
    px2deg=0.01,
    sampling_rate=1000.0,
)


def test_no_saccade():
    samp = np.random.randn(1000)
    data = ut.expand_samp(samp, y=0.0)
    clf = d.EyegazeClassifier(**common_args)
    p = clf.preproc(data, savgol_length=0.0, dilate_nan=0)
    # the entire segment is labeled as a fixation
    events = clf(p)
    assert len(events) == 1
    print(events)
    assert events[0]['end_time'] - events[0]['start_time'] == 1.0
    assert events[0]['label'] == 'FIXA'

    # missing data split events
    p[500:510]['x'] = np.nan
    events = clf(p)
    assert len(events) == 2
    assert np.all([e['label'] == 'FIXA' for e in events])

    # size doesn't matter
    p[500:800]['x'] = np.nan
    assert len(clf(p)) == len(events)


def test_one_saccade():
    samp = ut.mk_gaze_sample()

    data = ut.expand_samp(samp, y=0.0)
    clf = d.EyegazeClassifier(**common_args)
    p = clf.preproc(data, dilate_nan=0)
    events = clf(p)
    assert events is not None
    # we find at least the saccade
    events = ut.events2df(events)
    assert len(events) > 2
    if len(events) == 4:
        # full set
        assert list(events['label']) == ['FIXA', 'ISAC', 'ILPS', 'FIXA'] or \
            list(events['label']) == ['FIXA', 'ISAC', 'IHPS', 'FIXA']
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
    clf = d.EyegazeClassifier(
        max_initial_saccade_freq=.2,
        **common_args)
    p = clf.preproc(data, dilate_nan=0)
    events = clf(p)
    events = ut.events2df(events)
    # there is no PSO detected
    assert list(events['label']) == ['FIXA', 'SACC', 'FIXA']


def test_real_data():
    data = np.recfromcsv(
        'inputs/raw_eyegaze/sub-09/ses-movie/func/sub-09_ses-movie_task-movie_run-2_recording-eyegaze_physio.tsv.gz',
        #'inputs/raw_eyegaze/sub-02/ses-movie/func/sub-02_ses-movie_task-movie_run-5_recording-eyegaze_physio.tsv.gz',
        delimiter='\t',
        names=['x', 'y', 'pupil', 'frame'])

    clf = d.EyegazeClassifier(
        px2deg=0.0185581232561,
        sampling_rate=1000.0)
    p = clf.preproc(data)

    events = clf(
        p[:50000],
        #p,
    )

    events = ut.events2df(events)

    labels = list(events['label'])
    # find find all kinds of events
    for t in ('FIXA', 'PURS', 'SACC', 'LPSO', 'HPSO',
              'ISAC', 'ILPS', 'IHPS'):
        assert t in labels

    #ut.show_gaze(pp=p[:50000], events=events, px2deg=0.0185581232561)
    #ut.show_gaze(pp=p, events=events, px2deg=0.0185581232561)
    #import pylab as pl
    #saccades = events[events['label'] == 'SACC']
    #isaccades = events[events['label'] == 'ISAC']
    #print('#saccades', len(saccades), len(isaccades))
    #pl.plot(saccades['amp'], saccades['peak_vel'], '.', alpha=.3)
    #pl.plot(isaccades['amp'], isaccades['peak_vel'], '.', alpha=.3)
    #pl.show()
