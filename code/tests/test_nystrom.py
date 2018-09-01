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


def test_target_data():
    label_remap = {
        1: 'FIXA',
        2: 'SACC',
        3: 'PSO',
    }
    clf = d.EyegazeClassifier(**common_args)
    data = np.recfromcsv(
        'inputs/nystrom_target/1_2.csv',
        usecols=[1, 2, 3, 4])
    events = []
    ev_type = None
    ev_start = None
    vels = []
    for i in range(len(data)):
        s = data[i]
        if ev_type is None and s['event_type'] in (1, 2):
            ev_type = s['event_type']
            ev_start = i
        elif ev_type is not None and s['event_type'] != ev_type:
            amp, pv, medvel, avgvel = clf._get_signal_props(data[ev_start:i])
            events.append(dict(
                id=len(events),
                label=label_remap.get(ev_type),
                start_time=0.0 if ev_start is None else
                float(ev_start) / common_args['sampling_rate'],
                end_time=float(i) / common_args['sampling_rate'],
                peak_vel=pv,
                amp=amp,
            ))
            vels = []
            ev_type = s['event_type'] if s['event_type'] in (1, 2) else None
            ev_start = i
        if ev_type:
            vels.append(s['vel'])
    ut.show_gaze(pp=data, events=events, **common_args)
    #for e in events:
    #    print(e)
    import pylab as pl
    events = ut.events2df(events)
    saccades = events[events['label'] == 'SACC']
    isaccades = events[events['label'] == 'ISAC']
    print('#saccades', len(saccades), len(isaccades))
    pl.plot(saccades['amp'], saccades['peak_vel'], '.', alpha=.3)
    pl.plot(isaccades['amp'], isaccades['peak_vel'], '.', alpha=.3)
    pl.show()

def test_real_data():
    data = np.recfromcsv(
        'inputs/event_detector_1.1/1_2.csv',
        usecols=[0, 1])
    # when both coords are zero -> missing data
    data[np.logical_and(data['x'] == 0, data['y'] == 0)] = (np.nan, np.nan)

    clf = d.EyegazeClassifier(
        min_intersaccade_duration=0.04,
        # high threshold, static stimuli, should not have pursuit
        max_fixation_amp=4.0,
        **common_args)
    p = clf.preproc(data, dilate_nan=0.03)

    events = clf(p)

    # TODO compare against output from original matlab code
    #return
    for e in events:
        print('{:.4f} -> {:.4f}: {} ({})'.format(
            e['start_time'], e['end_time'], e['label'], e['id']))

    ut.show_gaze(pp=p, events=events, **common_args)
    import pylab as pl
    events = ut.events2df(events)
    saccades = events[events['label'] == 'SACC']
    isaccades = events[events['label'] == 'ISAC']
    print('#saccades', len(saccades), len(isaccades))
    pl.plot(saccades['amp'], saccades['peak_vel'], '.', alpha=.3)
    pl.plot(isaccades['amp'], isaccades['peak_vel'], '.', alpha=.3)
    pl.show()
