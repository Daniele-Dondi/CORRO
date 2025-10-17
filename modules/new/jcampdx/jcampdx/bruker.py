import numpy as np
import nmrglue as ng

# digital filter functions
# copied from nmrglue
# modfifed rm_dig_filter to test for dsp = 0,-1

bruker_dsp_table = {
    10: {
        2    : 44.75,
        3    : 33.5,
        4    : 66.625,
        6    : 59.083333333333333,
        8    : 68.5625,
        12   : 60.375,
        16   : 69.53125,
        24   : 61.020833333333333,
        32   : 70.015625,
        48   : 61.34375,
        64   : 70.2578125,
        96   : 61.505208333333333,
        128  : 70.37890625,
        192  : 61.5859375,
        256  : 70.439453125,
        384  : 61.626302083333333,
        512  : 70.4697265625,
        768  : 61.646484375,
        1024 : 70.48486328125,
        1536 : 61.656575520833333,
        2048 : 70.492431640625,
    },
    11: {
        2    : 46.,
        3    : 36.5,
        4    : 48.,
        6    : 50.166666666666667,
        8    : 53.25,
        12   : 69.5,
        16   : 72.25,
        24   : 70.166666666666667,
        32   : 72.75,
        48   : 70.5,
        64   : 73.,
        96   : 70.666666666666667,
        128  : 72.5,
        192  : 71.333333333333333,
        256  : 72.25,
        384  : 71.666666666666667,
        512  : 72.125,
        768  : 71.833333333333333,
        1024 : 72.0625,
        1536 : 71.916666666666667,
        2048 : 72.03125
    },
    12: {
        2    : 46.,
        3    : 36.5,
        4    : 48.,
        6    : 50.166666666666667,
        8    : 53.25,
        12   : 69.5,
        16   : 71.625,
        24   : 70.166666666666667,
        32   : 72.125,
        48   : 70.5,
        64   : 72.375,
        96   : 70.666666666666667,
        128  : 72.5,
        192  : 71.333333333333333,
        256  : 72.25,
        384  : 71.666666666666667,
        512  : 72.125,
        768  : 71.833333333333333,
        1024 : 72.0625,
        1536 : 71.916666666666667,
        2048 : 72.03125
    },
    13: {
        2    : 2.75,
        3    : 2.8333333333333333,
        4    : 2.875,
        6    : 2.9166666666666667,
        8    : 2.9375,
        12   : 2.9583333333333333,
        16   : 2.96875,
        24   : 2.9791666666666667,
        32   : 2.984375,
        48   : 2.9895833333333333,
        64   : 2.9921875,
        96   : 2.9947916666666667
    }
}


def remove_digital_filter(dic, data, truncate=True, post_proc=False):
    #from nmrglue

    if '$DECIM' not in dic:
        raise ValueError("dictionary does not contain DECIM parameter")
    decim = int(dic['$DECIM'][0].strip())

    if '$DSPFVS' not in dic:
        raise ValueError("dictionary does not contain DSPFVS parameter")
    dspfvs = int(dic['$DSPFVS'][0].strip())

    if '$GRPDLY' not in dic:
        grpdly = 0
    else:
        grpdly = float(dic['$GRPDLY'][0].strip())

    print("DECIM", decim, "DSP", dspfvs, "GRPDLY", grpdly)

    return rm_dig_filter(data, decim, dspfvs, grpdly, truncate, post_proc)


def rm_dig_filter(
        data, decim, dspfvs, grpdly=0, truncate_grpdly=True, post_proc=False):
    #from nmrglue

    import nmrglue as ng

    if grpdly > 0:  # use group delay value if provided (not 0 or -1)
        phase = grpdly

    # determine the phase correction
    else:
        if dspfvs >= 14:    # DSPFVS greater than 14 give no phase correction.
            phase = 0.
        elif dspfvs <= 0: # older AMX spectrometer?
            phase = 0.
        else:   # loop up the phase in the table
            if dspfvs not in bruker_dsp_table:
                raise ValueError("dspfvs not in lookup table (%s)"%dspfvs)
            if decim not in bruker_dsp_table[dspfvs]:
                raise ValueError("decim not in lookup table (%s)"%decim)
            phase = ng.bruker.bruker_dsp_table[dspfvs][decim]

    if truncate_grpdly:     # truncate the phase
        phase = np.floor(phase)

    # and the number of points to remove (skip) and add to the beginning
    skip = int(np.floor(phase + 2.))    # round up two integers
    add = int(max(skip - 6, 0))           # 6 less, or 0

    # DEBUG
    # print("phase: %f, skip: %i add: %i"%(phase,skip,add))

    if post_proc:
        s = data.shape[-1]
        pdata = data * np.exp(2.j * np.pi * phase * np.arange(s) / s)
        pdata = pdata.astype(data.dtype)
        return pdata

    else:
        # frequency shift
        pdata = ng.proc_base.fsh2(data, phase)

        # add points at the end of the specta to beginning
        pdata[..., :add] = pdata[..., :add] + pdata[..., :-(add + 1):-1]
        # remove points at end of spectra
        return pdata[..., :-skip]
