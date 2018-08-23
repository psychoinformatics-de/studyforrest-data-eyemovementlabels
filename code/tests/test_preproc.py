import numpy as np
from . import utils as ut
from .. import preprocess_eyegaze_recordings as pp


common_args = dict(
    px2deg=0.0185581232561,
    sampling_rate=1000.0,
)


def test_preproc():
    samp = np.random.randn(1000)
    data = ut.expand_samp(samp, y=0.0)
    p = pp.preproc(data, savgol_length=0.019, savgol_polyord=1, **common_args)
    # first values are always zero
    assert p[0]['vel'] == 0
    assert p[0]['accel'] == 0
    p = p['x']
    # shorter filter leaves more "noise"
    p_linshort = pp.preproc(data, savgol_length=0.009, savgol_polyord=1,
                            **common_args)['x']
    assert np.std(p) < np.std(p_linshort)
    # more flexible filter leaves more "noise"
    p_quad = pp.preproc(data, savgol_length=0.019, savgol_polyord=2,
                        **common_args)['x']
    assert np.std(p) < np.std(p_quad)

    # insert small NaN patch
    data['x'][100:110] = np.nan
    assert np.sum(np.isnan(data['x'])) == 10
    p = pp.preproc(data, savgol_length=0.019, savgol_polyord=1,
                   min_blink_duration=10.0, **common_args)['x']
    # the original data does NOT change!
    assert np.sum(np.isnan(data['x'])) == 10
    # the gap will widen
    assert np.sum(np.isnan(p)) == 28
    # a wider filter will increase the gap, actual impact depends on
    # filter setup
    p = pp.preproc(data, savgol_length=0.101, savgol_polyord=1,
                   min_blink_duration=10.0, **common_args)['x']
    assert np.sum(np.isnan(p)) > 28
    # no widen the gap pre filtering (disable filter to test that)
    p = pp.preproc(data, savgol_length=0.001, savgol_polyord=0,
                   min_blink_duration=0.0, dilate_nan=0.015,
                   **common_args)['x']
    # the original data still does NOT change!
    assert np.sum(np.isnan(data['x'])) == 10
    # the gap will widen
    assert np.sum(np.isnan(p)) == 10 + 2 * 15

    # insert another small gap that we do not want to widen
    data['x'][200:202] = np.nan
    assert np.sum(np.isnan(data['x'])) == 12
    p = pp.preproc(data, savgol_length=0.001, savgol_polyord=0,
                   min_blink_duration=0.008, dilate_nan=0.015,
                   **common_args)['x']
    assert np.sum(np.isnan(p)) == 10 + 2 * 15 + 2

    samp = [0.0, 2.0]
    data = ut.expand_samp(samp, y=0.0)
    p = pp.preproc(data, px2deg=1.0, savgol_length=0, dilate_nan=0,
                   sampling_rate=10.0)
    # 2 deg in 0.1s -> 20deg/s
    assert p['vel'][-1] == 20
    assert p['accel'][-1] == 200

    data['x'][1] = 200
    p = pp.preproc(data, px2deg=1.0, savgol_length=0, dilate_nan=0,
                   sampling_rate=10.0)
    assert p['vel'][-1] == 0
    assert p['accel'][-1] == 0
