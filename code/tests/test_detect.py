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


def test_one_saccade():
    samp = ut.mk_gaze_sample()

    data = ut.expand_samp(samp, y=0.0)
    p = pp.preproc(data, savgol_length=0.019, dilate_nan=0, **common_args)
    events = detect(p, 50.0, **common_args)
    assert events is not None
    # we find at least the saccade
    assert len(events) > 1
    assert events['label'][0] == 'SACCADE'
