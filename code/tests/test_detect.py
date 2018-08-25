import numpy as np
from . import utils as ut
from .. import preprocess_eyegaze_recordings as pp
from ..detect_events import detect


common_args = dict(
    px2deg=0.01,
    sampling_rate=1000.0,
)


def test_no_saccade():
    samp = np.random.randn(1001)
    data = ut.expand_samp(samp, y=0.0)
    p = pp.preproc(data, savgol_length=0.0, dilate_nan=0, **common_args)
    # the entire segment is labeled as a fixation
    events = detect(p, 50.0, **common_args)
    assert len(events) == 1
    assert events[0]['duration'] == 1.0
    assert events[0]['label'] == 'FIX'

    # little missing data makes no diff
    p[500:510] = np.nan
    events = detect(p, 50.0, **common_args)
    assert len(events) == 1
    assert events[0]['duration'] == 1.0
    assert events[0]['label'] == 'FIX'

    # but more kills it, TODO why?
    p[500:550] = np.nan
    assert detect(p, 50.0, **common_args) is None


def test_one_saccade():
    samp = ut.mk_gaze_sample()

    data = ut.expand_samp(samp, y=0.0)
    nospikes = pp.filter_spikes(data.copy())
    p = pp.preproc(
        nospikes, savgol_length=0.019, savgol_polyord=2,
        dilate_nan=0, **common_args)
    events = detect(p, 50.0, **common_args)
    assert events is not None
    # we find at least the saccade
    assert len(events) == 4
    assert list(events['label']) == ['FIX', 'SACCADE', 'GLISSADE', 'FIX']
    for i in range(0, len(events) - 1):
        # complete segmentation
        assert events['start_time'][i + 1] == events['end_time'][i]
