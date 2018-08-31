import numpy as np
from . import utils as ut
from .. import detect_events as d


common_args = dict(
    # we don't know what the stimulus props are
    # variant1
    #px2deg=d.deg_per_pixel(0.516, 0.6, 1024),
    #sampling_rate=500.0,
    # variant2
    px2deg=d.deg_per_pixel(0.377, 0.67, 1024),
    sampling_rate=1250.0,
)


def test_real_data():
    data = np.recfromcsv(
        'inputs/event_detector_1.1/1_13.csv',
        usecols=[0, 1])
    # when both coords are zero -> missing data
    data[np.logical_and(data['x'] == 0, data['y'] == 0)] = (np.nan, np.nan)

    clf = d.EyegazeClassifier(
        min_intersaccade_duration=0.04,
        **common_args)
    p = clf.preproc(data, dilate_nan=0.03)

    events = clf(p)

    for e in events:
        print('{:.2f} -> {:.2f}: {} ({})'.format(
            e['start_time'], e['end_time'], e['label'], e['id']))
    ut.show_gaze(pp=p, events=events, **common_args)
    import pylab as pl
    import pandas as pd
    events = pd.DataFrame(events)
    saccades = events[events['label'] == 'SACC']
    isaccades = events[events['label'] == 'ISAC']
    print('#saccades', len(saccades), len(isaccades))
    pl.plot(saccades['amp'], saccades['peak_vel'], '.', alpha=.3)
    pl.plot(isaccades['amp'], isaccades['peak_vel'], '.', alpha=.3)
    pl.show()
