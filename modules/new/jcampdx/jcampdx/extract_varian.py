import nmrglue as ng
import numpy as np
import os, sys
from scipy.optimize import curve_fit


"""
python functions to read and re-process 1D or 2D vnmr format files

not all processing steps are replicated

running this script directly displays a matplotlib plot
"""

def shear_45(udic, data):

    #shear/rotate data 45 degrees (for jres)
    #do before discarding imaginaries
    #but after lp/zf processing

    sw_x = udic[1]['sw']
    sw_y = udic[0]['sw']

    np_x = udic[1]['size']
    np_y = udic[0]['size']

    uc = ng.fileiobase.uc_from_udic(udic, 1)

    horiz_off_pt_per_row = (sw_y/np_y)(sw_x/np_x)

    start_top = int(np_y/2)   if np_y%2 else int(np_y/2+0.5)
    start_btm = int(np_y/2-1) if np_y%2 else int(np_y/2-1.5)

    data = ng.proc_base.ifft(data)

    for i in range(start_top, np_y, 1):
        offset_pts = (i-start_top+1) * horiz_off_pt_per_row
        data[i] = ng.proc_base.ps(data[i], 0, -offset_pts*360)

    for i in range(start_btm, -1, -1):
        offset_pts = (start_btm-i+1) * horiz_off_pt_per_row
        data[i] = ng.proc_base.ps(data[i], 0, +offset_pts*360)
    
    data = ng.proc_base.fft(data)

    return data


def get_2d_coef(udic, procpar):

    """
    extract f1coef or f2coef from procpar

    RR1 IR1 RR2 IR2 ... RI1 II1 RI2 II2 ...
    IR2: imag(I) part of 2nd(2) fid added to real(R) part of final 2d array
    """
    coef = ""

    vnmr_idx = str(udic[0]['procdim'])

    coef_str = "f%scoef"%vnmr_idx

    if coef_str in procpar:
        coef = procpar[coef_str]['values'][0]

    if not coef:
        coef = default_coef(udic, procpar)

    return coef

def default_coef(udic, procpar):

    """
    assume either states or magnitude spectra if f1coef=""

    todo:
    imag may not need to be flipped for some spectra (non-biopack?)
    """

    #print('no coef, guessing default')

    phase_str = ""

    #print(procpar['array']['values'])

    for arr_var in procpar['array']['values']:
        if arr_var.startswith('phase'):
            if len(procpar[arr_var]['values']) > 1:
                phase_str = arr_var

    if not phase_str:
        return None

    phase = procpar[phase_str]['values']

    coef = None

    if phase:
        if len(phase) == 2:
            coef = "1 0 0 0 0 0 -1 0"
        else:
            coef = "1 0 0 -1"

    return coef

def split_coef(coef):

    #parse coefficent string

    coef = list(map(float, coef.split()))
    coef = np.array(coef)

    coef_to_r = coef[:coef.size//2]
    coef_to_i = coef[coef.size//2:]

    RR = coef_to_r[0::2]
    IR = coef_to_r[1::2]
    RI = coef_to_i[0::2]
    II = coef_to_i[1::2]

    return RR, IR, RI, II


def block_diag(arr, num):
    #block diagonal array of n arr blocks
    rows, cols = arr.shape
    result = np.zeros((num * rows, num * cols), dtype=arr.dtype)
    for k in range(num):
        result[k * rows:(k + 1) * rows, k * cols:(k + 1) * cols] = arr
    return result

def apply_f1coef(data, udic, procpar):

    #use coef to shuffle 2d data after f2 processing

    data_r = data.real
    data_i = data.imag

    coef = get_2d_coef(udic, procpar)
    #print('f1coef', coef)

    if coef is None:
        return data

    RR, IR, RI, II = split_coef(coef)

    ysize = data.shape[0]//RR.size

    result_r =  block_diag(RR[None,:], ysize).dot(data_r)
    result_r += block_diag(IR[None,:], ysize).dot(data_i)
   
    result_i =  block_diag(RI[None,:], ysize).dot(data_r)
    result_i += block_diag(II[None,:], ysize).dot(data_i)

    return result_r + 1j*result_i





def contour_levels(data, scale=20, factor=1.1, number=20, 
                    threshold=None, linear=False, show='all'):

    #for matplotlib plotting
    
    _2d_min = np.min(data.real)
    _2d_max = np.max(data.real)

    if threshold > 0:
        start = np.abs(threshold)
    else:
        start = np.max((_2d_max, _2d_min))/scale

    if not linear:
        pos_levels =  start +  start*np.arange(number)**factor
        neg_levels = -start + -start*np.arange(number)**factor
    else:
        pos_levels =  start +  np.arange(number)*( start*factor - start)
        neg_levels = -start + -np.arange(number)*(-start*factor + start)

    if show == 'neg':
        levels = np.sort(neg_levels)
        color = ['red']*number
    elif show == 'pos':
        levels = np.sort(pos_levels)
        color = ['blue']*number
    else:
        levels = np.sort(np.concatenate((pos_levels,neg_levels)))
        color = ['red']*number + ['blue']*number

    return levels, color

def est_lw(x, fid, sfrq):

    #finds average linewidth of spectrum
    #fits cumulative sum of the (real) FID envelope

    fidsum = np.cumsum(np.abs(fid.real))

    idx1 = np.argmin(np.abs(fidsum - np.max(fidsum)*0.8))
    cst1 =  (fidsum[idx1]-fidsum[0])/(x[idx1]-x[0])
    guess = [np.max(fidsum), cst1, 1]
    f = lambda x,a,b,R: a - b*np.exp(-R*x)

    popt, pcov = curve_fit(f, x, fidsum, p0=guess)

    return popt[-1]/np.pi

def noise_std(y, binsize=100):

    #find noise level (1 std) by binning

    y = y.real

    noise_std = []

    for i in range(y.size//binsize):
        noise_std.append( np.std(y[i*binsize:i*binsize+binsize]) )

    return np.median(noise_std)


def noise_std_2d(data, binsize=100):

    #find noise level (1 std) by binning

    noise_std = []

    data = data.real
    x, y = data.shape[0]//binsize, data.shape[1]//binsize

    for i, j in np.ndindex((x+1, y+1)):
        xst, xend = binsize*i, binsize*i+binsize
        yst, yend = binsize*j, binsize*j+binsize
        block = data[xst:xend,yst:yend]
        std = np.std(block)
        noise_std.append(std)

    return np.median(noise_std)


def calc_digfilter(ntaps, decfactor, norm=False):

    #blackman filter
    #copied from openvnmrj

    ntaps = int(ntaps)
    decfactor = int(decfactor)

    dbuffer = np.zeros(ntaps)
    p1 = 0 #*tmpfilter
    p2 = 0+ntaps #*tmpfilter2
    wc = np.pi/decfactor
    sum = 0.0
    nfullpts = ntaps

    _max = int((ntaps+1)/2)
    for i in range(_max):

        j=i-_max+1
        hd = np.sin(wc*j)/(np.pi*j) if j else 1/decfactor
        arg1 = (2*np.pi) / (nfullpts-1)
        w = 0.42 - 0.5*np.cos(arg1*i) + 0.08*np.cos(2*arg1*i)
        dbuffer[p1] = hd*w
        p2 -= 1
        dbuffer[p2] = dbuffer[p1]
        sum += dbuffer[p1]
        p1 += 1
        if p1-1 != p2:
            sum += dbuffer[p2]

    if norm:
        dbuffer /= sum;

    return dbuffer, sum

def has_param(key, dic):

    if key in dic:
        return True
    
    return False

def is_array_param(key, dic):

    if key in dic:
        if len(dic[key]['values']) > 1:
            return True
    
    return False


def get_param(key, dic):

    if key not in dic:
        return None

    values = dic[key]['values']

    if len(values) > 1:
        return values
    else:
        return values[0]

def conv(val, dtype):

    try:
        return dtype(val)
    except:
        return val


def conv_arr(values, dtype):

    result = []

    for s in values:
        
        try:
            result.append(dtype(s))
        except:
            result.append(s)

    return result

def get_dim(dic):

    #determine dimensionaly of spectrum using procpar file

    ndim = 1

    try:
        ni = int(dic['procpar']['ni3']['values'][0])
        if ni > 1:
            ndim += 1
    except:
        pass

    try:
        ni = int(dic['procpar']['ni2']['values'][0])
        if ni > 1:
            ndim += 1
    except:
        pass

    try:
        ni = int(dic['procpar']['ni']['values'][0])
        if ni > 1:
            ndim += 1
    except:
        pass

    return ndim

def varian_to_udic(dic, udic):

    #extract propar params and place in correct dimension of udic

    """
    expand dispaly axis parameter
    """


    procpar = dic['procpar']

    ndim = get_dim(dic)
    if ndim != udic['ndim']:
        raise ValueError('ambiguous number of dimensions')

    channels = {}

    sfrq = conv(get_param("sfrq", procpar), float)
    tn = get_param("tn", procpar)

    channels["0"] = (tn, sfrq, "ppm", 0)

    for s in ["1", "2", "3", "4"]:

        label_par = "dn" + s.replace("1", "")
        freq_par = "dfrq" + s.replace("1", "")

        label = get_param(label_par, procpar)
        freq = get_param(freq_par, procpar)

        channels[s] = (label, freq, "ppm", int(s))


    mapping = {"1":channels["1"], 
               "2":channels["2"], 
               "3":channels["3"], 
               #"c":('cm', 1, 'cm', 0), 
               "d":channels["1"], 
               "h":('Hz', 1, 'Hz', 0), 
               #"k":('kHz', 1, 'kHz', 0),
               #"m":('mm', 1, 'mm', 0), 
               "n":("", 1, "", 0), 
               "p":channels["0"],
               #"u":('um', 1, 'um', 0),
                }

    spec_axis = get_param("axis", procpar)
    axis_labels = [mapping[c] for c in spec_axis][::-1] #sort in nmrglue order

    for i in range(ndim):
        udic[i]['label'] = axis_labels[i][0]
        udic[i]['obs'] = conv(axis_labels[i][1], float)
        udic[i]['units'] = axis_labels[i][2]
        udic[i]['channel'] = axis_labels[i][3]

    """
    get other basic values for each dimension
    check proc: if 'n' (no ft) skip dimension (biopack?)
    """
    params = ['sw', 'rfp', 'rfl', 'ni', 'rp', 'lp', 
               "fn", 'dmg', "ssfilter", 'proc',
               "lpopt", "lpfilt", "lpnupts", "strtlp", "lpext", "strtext",
              ]

    vnmr_idx = 0 #0, 1, 2
    udic_idx = ndim-1 #2, 1, 0

    while udic_idx >= 0:

        udicidx = udic_idx
        vnmridx = str(vnmr_idx)

        proc = get_param("proc"+vnmridx.replace("0", ""), procpar)
        if proc == "n":
            vnmr_idx += 1
            continue
        if proc == "ht":
            raise ValueError('Hadamard spectroscopy not supported')

        udic[udicidx]['procdim'] = int(vnmridx)

        for p in params:

            _p = p + vnmridx.replace("0", "")

            if _p == "ni":  _p = "np"
            if _p == "ni1": _p = "ni"

            val = get_param(_p, procpar)
            if p in ("ni", "fn"):
                val = conv(val, int)
            else:
                val = conv(val, float)


            udic[udicidx][p] = val

        """ 
        reference
        """
        rfp = udic[udicidx]['rfp']
        rfl = udic[udicidx]['rfl']
        udic[udicidx]['car'] = udic[udicidx]['sw']/2 - rfl + rfp

        #next dimension
        udic_idx -= 1
        vnmr_idx += 1

    """
    other
    """

    udic["pulseseq"] = get_param("seqfil", procpar)
    udic["solvent"] = get_param("solvent", procpar)

    return

def test_key(key, dic):

    if key in dic:
        if dic[key] and (dic[key] != 'n'):
            return True
    return False


def test_value(value, zero_is_false=False):

    if value in ("", "n", None):
        return False

    if zero_is_false and value==0:
        return False

    return True

def get_value(key, dic):

    if key not in dic:
        return None
    else:
        return dic[key]

def signal_to_noise(x, y, noise):

    #signal to noise ratio
    #noise is the std dev of the noise
    #calculated as 2.5 * height of signal / (5 * sd of noise)
    #http://www.ebyte.it/library/docs/ExperimentalNoise79/ExpNoise79.html

    y = y.real

    waterwin = (x > 4) & (x < 6)

    maxnonwaterpos = np.argmax(np.abs(y[~waterwin]))
    maxnonwater = np.abs(y[~waterwin][maxnonwaterpos])

    maxallpos = np.argmax(np.abs(y))
    maxall = np.abs(y[maxallpos])

    if maxnonwater > (5 * noise):
        signal = maxnonwater
    else:
        signal = maxall

    return 2.5 * signal / (5 * noise)

def lin_pred_loop(data, udic, udic_dim):

    #linear pred if lpopt is arrayed

    lpopt = udic[udic_dim]['lpopt']
    lpfilt = udic[udic_dim]['lpfilt']
    lpnupts = udic[udic_dim]['lpnupts']
    strtlp = udic[udic_dim]['strtlp']
    lpext = udic[udic_dim]['lpext']
    strtext = udic[udic_dim]['strtext']

    for i in range(len(lpopt)):

        lpfilt_curr = int(lpfilt[i])
        lpnupts_curr = int(lpfilt[i])
        strtlp_curr = int(strtlp[i])
        lpext_curr = int(lpext[i])
        strtext_curr = int(strtext[i])

        #print('lpfilt coeffs', lpfilt_curr)
        #print('lpnupts using #pts', lpnupts_curr)
        #print('strtlp starting at pts', strtlp_curr)
        #print('lpext extending #pts', lpext_curr)
        #print('strtext starting at pts', strtext_curr)

        if lpfilt_curr > 8:
            #print('resetting lpfilt to 8')
            lpfilt_curr = 8

        if lpopt[i] == 'b':
            #print('backwards linear prediction')

            if strtext_curr != lpext_curr:
                #print('lpext and strtext not equal, assume strtext=lpext')
                pass

            new_data = data[..., lpext_curr:]
            pred_slice = slice(0, lpnupts_curr)

            data_lp = ng.proc_lp.lp(new_data, pred=lpext_curr, slice=pred_slice, 
                                order=lpfilt_curr, mode='bf', append='before')

            data = data_lp
            udic[udic_dim]['size'] = data.shape[-1]

        elif lpopt[i] == "f":
            #print('forward linear prediction')

            if strtext_curr+lpext_curr < data.shape[-1]:
                #print('lpext ends before data, data will be truncated')
                pass

            new_data = data[..., :strtext_curr-1]
            pred_slice = slice(strtlp_curr-lpnupts_curr, strtlp_curr+1)

            data_lp = ng.proc_lp.lp(new_data, pred=lpext_curr, slice=pred_slice, 
                                order=lpfilt_curr, mode='fb', append='after')

            data = data_lp
            udic[udic_dim]['size'] = data.shape[-1]

    return data

def lin_pred_single(data, udic, udic_dim):

    #linear pred if lpopt is single value
    #nmrglue linear prediction may not very good with high order

    lpopt = udic[udic_dim]['lpopt']
    lpfilt = int(udic[udic_dim]['lpfilt'])
    lpnupts = int(udic[udic_dim]['lpnupts'])
    strtlp = int(udic[udic_dim]['strtlp'])
    lpext = int(udic[udic_dim]['lpext'])
    strtext = int(udic[udic_dim]['strtext'])

    #print('lpfilt coeffs', lpfilt)
    #print('lpnupts using #pts', lpnupts)
    #print('strtlp starting at pts', strtlp)
    #print('lpext extending #pts', lpext)
    #print('strtext starting at pts', strtext)

    if lpfilt > 8:
        #print('resetting lpfilt to 8')
        lpfilt = 8

    if lpopt == 'b':
        #print('backwards linear prediction')

        if strtext != lpext:
            #print('lpext and strtext not equal, assume strtext=lpext')
            pass

        new_data = data[..., lpext:]
        pred_slice = slice(0, lpnupts)

        data_lp = ng.proc_lp.lp(new_data, pred=lpext, slice=pred_slice, 
                            order=lpfilt, mode='bf', append='before')

        data = data_lp
        udic[udic_dim]['size'] = data.shape[-1]


    elif lpopt == "f":
        #print('forward linear prediction')

        if strtext-1+lpext < data.shape[-1]:
            #print('lpext ends before data, data will be truncated')
            pass

        new_data = data[..., :strtext-1]
        pred_slice = slice(strtlp-lpnupts, strtlp+1)

        data_lp = ng.proc_lp.lp(new_data, pred=lpext, slice=pred_slice, 
                            order=lpfilt, mode='fb', append='after')

        data = data_lp
        udic[udic_dim]['size'] = data.shape[-1]

    return data


def lin_pred(data, udic, udic_dim):

    #linear prediction

    lpopt = udic[udic_dim]['lpopt']

    if type(lpopt) is list:

        data = lin_pred_loop(data, udic, udic_dim)

    else:

        data = lin_pred_single(data, udic, udic_dim)

    return data

def process(dic, data, udic,):

    #nmrglue ppm_scale returns high to low ppm

    #imag NOT flipped
    #proc_base.fft returns dss on right
    #fid phase > 0 + fft = upfield (right) shift
    #p0=-rp, p1=lp

    #print('data size', data.shape)


    ndim = udic['ndim']
    #print('ndim', ndim)
    lastdim = ndim-1

    npts = udic[lastdim]['size']
    sw = udic[lastdim]['sw']
    obs = udic[lastdim]['obs']
    center = udic[lastdim]['car']
    solvent = udic['solvent']
    pulseseq = udic['pulseseq']
    #print('pulse', pulseseq)
    #print('solv', solvent)

    #if not phase senstive - set display to absolute value
    coef = get_param("f1coef", dic['procpar'])
    if coef:
        coef = list(map(float, coef.split()))
        coef = np.array(coef)
        if (coef.size < 8):
            udic[1]['dmg'] = 'av'
            udic[0]['dmg'] = 'av1'
    dmg = get_value("dmg", udic[lastdim])

    #print('size', npts, 'sw', sw, 'obs', obs, 'car', center, center/obs)


    #do water suppression (only at center) if ssfilter active
    #dont use vnmr parameters for now
    water_txt = ('h2o', 'd2o', 'h20', 'd20', 'water', 'oxide')
    is_water = any(s in solvent.lower() for s in water_txt)

    if test_key("ssfilter", udic[lastdim]) and is_water:
        #print('solvent subtraction')
        taps = 121 if npts/2 > 121 else int(npts/4)
        wid = int(sw/100 + 0.5)
        filt_win, _ = calc_digfilter(taps, wid)
        filt_data = ng.proc_bl.sol_general(data, filt_win)
        data = filt_data

    #linear prediction
    if udic[lastdim]['proc'] == "lp":
        data = lin_pred(data, udic, lastdim)

    #first point mult (dont use vnmr param fpmult for now)
    data[...,0] *= 0.5

    #print('exp weighting')
    try:
        t = ng.fileiobase.uc_from_udic(udic, lastdim).sec_scale()
        lw = est_lw(t, np.atleast_2d(data)[0], obs)
        #print('est lw for lb', lw)
    except:
        lw = 1.0
    data = ng.proc_base.em(data, lw/sw)

    if ndim > 1:
        #print('cosine weighting')
        if dmg.startswith('av') or dmg.startswith('pwr'):
            #print("using sine bell")
            off = 0
        else:
            off = 0.5
        data = ng.proc_base.sp(data, off, 1, 2) #cosine

    zf = get_value("fn", udic[lastdim])
    #print('zerofill')
    if zf < data.shape[-1]:
        data = data[...,:zf]
    elif zf > data.shape[-1]:
        data = ng.proc_base.zf(data, zf)
    udic[lastdim]['size'] = data.shape[-1]

    #print('ft')
    data = ng.proc_base.fft(data)
    udic[lastdim]['time'] = False
    udic[lastdim]['freq'] = True



    rp = -get_value("rp", udic[lastdim])
    lp = get_value("lp", udic[lastdim])
    #print('phase', rp, lp)
    data = ng.proc_base.ps(data, rp, lp)


    #autophase? hopefully vnmr parameters are close
    if ndim == 1:
        if not any(s in pulseseq.lower() for s in ('dept', 'apt')):
            #print('autophase')
            data, ph = ng.proc_autophase.autops(data, 'acme', return_phases=True)
            #print('phase adj', ph)

    #reference?
    #baseline correct?

    #done 1D
    if ndim == 1:
        #print('done 1d')
        return data

    #2D

    #print('shuffling')
    data = apply_f1coef(data, udic, dic['procpar'])

    #print('transpose')
    data = data.T
    lastdim -= 1

    if udic[lastdim]['proc'] == "lp":
        data = lin_pred(data, udic, lastdim)

    data[...,0] *= 0.5

    #print('cosine weighting')
    if dmg.startswith('av') or dmg.startswith('pwr'):
        #print("using sine bell")
        off = 0
    else:
        off = 0.3
    data = ng.proc_base.sp(data, off, 1, 2)

    zf = get_value("fn", udic[lastdim])
    #print('zerofill')
    if zf < data.shape[-1]:
        data = data[...,:zf]
    elif zf > data.shape[-1]:
        data = ng.proc_base.zf(data, zf)
    udic[lastdim]['size'] = data.shape[-1]


    #print('ft')
    data = ng.proc_base.fft(data)
    udic[lastdim]['time'] = False
    udic[lastdim]['freq'] = True

    rp = -get_value("rp", udic[lastdim])
    lp = get_value("lp", udic[lastdim])
    #print('phase', rp, lp)
    data = ng.proc_base.ps(data, rp, lp)

    #print('transpose')
    data = data.T
    lastdim += 1

    #reference?
    #baseline correction?

    #tilt for 2dj (and some others?)
    if "2dj" in pulseseq.lower():
        #print('tilting 2dj')
        data = shear_45(udic, data)

    #transform data for display
    dmg = get_value("dmg", udic[lastdim])
    if "av" in dmg:
        data = np.abs(data)
    elif "pwr" in dmg:
        data = np.abs(data)**2
    elif "pa" in dmg:
        data = numpy.arctan2(data.imag, data.real)

    #print('done 2d')
    return data

def get_processed_data(folder):

    #try reading data
    dic, data = ng.varian.read(folder)

    #for biopack, may get confused (psudo 3d?), reload as 2d
    ndim = get_dim(dic)
    if ndim == 2:
        dic, data = ng.varian.read(folder, as_2d=True)

    udic = ng.varian.guess_udic(dic, data)
    varian_to_udic(dic, udic)
    #print(udic)

    data = process(dic, data, udic)

    return udic, dic, data


if __name__ == "__main__":

    import matplotlib.pyplot as plt

    folder = sys.argv[1]


    """
    read and process
    """

    udic, dic, data = get_processed_data(folder)


    """
    plot
    """

    if ndim == 1:


        uc_x = ng.fileiobase.uc_from_udic(udic, 0)
        func = "%s_scale"%(udic[0]['units'].lower())
        x = getattr(uc_x, func)()

        plt.plot(x, data)
        plt.xlabel(udic[0]['label'])
        plt.gca().invert_xaxis()
        plt.show()

    if ndim == 2:

        std = 10

        uc_x = ng.fileiobase.uc_from_udic(udic, 1)
        func = "%s_scale"%(udic[1]['units'].lower())
        x = getattr(uc_x, func)()

        uc_y = ng.fileiobase.uc_from_udic(udic, 0)
        func = "%s_scale"%(udic[0]['units'].lower())
        y = getattr(uc_y, func)()

        noise = noise_std_2d(data)
        

        dmg = get_value("dmg", udic[1])
        if "av" in dmg:
            arg = 20, 1.1, 20, 2*noise*std, False, 'pos'
        elif "pwr" in dmg:
            arg = 20, 1.1, 20, 2*noise*std, False, 'pos'
        else:
            arg = 20, 1.1, 20, noise*std, False, 'all'
        
        contours, colors = contour_levels(data, *arg)

        plt.contour(x, y, data, levels=contours, colors=colors)
        plt.xlabel(udic[1]['label'])
        plt.ylabel(udic[0]['label'])
        plt.gca().invert_xaxis()
        plt.gca().invert_yaxis()
        plt.show()


