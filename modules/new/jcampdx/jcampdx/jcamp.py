import sys
import os
import string
import itertools
import datetime
import numpy as np
import multiprocessing

import parse, encode, decode
import jcampcs
import bruker

#TODO: 
#REMOVE GROUP DELAY!!!!!
#add something to parse/update .COUPLING CONSTANTS
#

#jcamp issues/wishlist:
#equivalent to nmrglue 'obs' (center freq in Mhz) and 'car' (center freq as ppm*obs) per dimension
#bruker 'offset' instead of 'car' may be okay
#ACQUISTION SCHEME, per dimension (would be needed for 3D, 4D...)
#should preacquistion DELAY include group delay? should group delay be removed before making jcamp?
#details about how data in interleaved (like varian) could be useful, or
#data is shuffled to a specific order before output

#add to udic:
#    format "bruker", "varian" etc...
#    solvent
#    temp
#    pulseseq

def quote_string(s, force=False):

    """
    Add jcamp-style delimiters to string
    """

    char = list(string.whitespace) + [",", ";"]

    if force or any(c in char for c in s):
        return "<" + s + ">"
    else:
        return s

def unquote_string(s):

    """
    Remove jcamp-style delimiters from string
    """

    if s.startswith("<") and s.endswith(">"):
        return s[1:-1].strip()
    else:
        return s

def write_line(key, val):

    """
    Write a jcamp LDR from a dictionary key and value
    Formatting depends on type of value
    """

    if isinstance(val, str):
        val = str(val)
    elif isinstance(val, float) or isinstance(val, int):
        val = str(val)
    elif isinstance(val, tuple):
        val = ", ".join(val)
    elif isinstance(val, list):
        try:
            val = "\n".join(val)
        except:
            val = "\n".join(map(str, val))
    elif isinstance(val, dict):
        val = write_dic(val)
    else:
        try:
            val = val.write()
        except:
            raise ValueError('unknown data type for LDR %s'%key)

    return "".join(["##", key, "=", val])

def write_dic(dic):

    """
    Write JCAMP LDRs from a dictionary
    """

    result = []

    for k,v in dic.items():

        if v is None: continue
        result.append(write_line(k, v))

    return "\n".join(result)

def blank_udic(ndim):

    """
    generates the default nmrglue udic
    """

    udic = {'ndim':ndim,}

    for i in range(ndim):

        udic[i] = { 'car':999.99, 
                    'complex':True, 
                    'encoding':'direct', 
                    'freq':False, 
                    'label':["X","Y","Z","A"][i], 
                    'obs':999.99, 
                    'size':1, 
                    'sw':999.99, 
                    'time':True,
                    'units':'hz',
                }

        if i < (ndim-1):
            udic[i]['encoding'] = 'states'

    return udic


class NucTable():

    """
    gyromagnetic ratios (MHz/T) and default spectrum carrier positions (ppm)
    for approximate frequency and referencing calculations
    """

    nuc = { "1H":{'gamma':42.57638474, 'default_car':4.8}, 
            "2H":{'gamma':6.536, 'default_car':4.8},
            "13C":{'gamma':10.7084, 'default_car':100.0},
            "15N":{'gamma':4.316, 'default_car':200.0},
            "31P":{'gamma':17.235, 'default_car':0.0},
            "19F":{'gamma':40.078, 'default_car':0.0},
            }

    @classmethod
    def get_nuc(cls, nucleus):
        if nucleus.startswith("^"):
            nucleus = nucleus[1:]
        return cls.nuc[nucleus]

    @classmethod
    def get_1h_field(cls, obs_freq, nucleus):
        return obs_freq / cls.get_nuc(nucleus)['gamma'] * cls.get_nuc("1H")['gamma']

    

class DateTime():

    """
    holds Jcamp data/time formats
    """

    dateformat = "%y/%m/%d"
    timeformat = "%H:%M:%S"
    longdatefmt = "%Y/%m/%d %H:%M:%S"

    @classmethod
    def date(cls, date=None):
        if not date:
            return datetime.datetime.now().date().strftime(cls.dateformat)
        else:
            return date.strftime(cls.dateformat)

    @classmethod
    def time(cls, time=None):
        if not time:
            return datetime.datetime.now().time().strftime(cls.timeformat)
        else:
            return time.strftime(cls.timeformat)

    @classmethod
    def longdate(cls, date=None):
        if not date:
            return datetime.datetime.now().strftime(cls.longdatefmt)
        else:
            return date.strftime(cls.dateformat)

class PeakAssignmentsData():

    """
    PEAK ASSIGNMENTS data table structure
    data: a list of lists, with one "group" per row
    units: required, but None can be used to suprress XUNITS, FIRSTX, etc

    method write() prints a JCAMP formatted string with the relevant LDRs
    """

    def __init__(self, data):

        self.data = data
        self.npts = len(data)
        self.dim = len(data[0])

        self.dataclass = "PEAK ASSIGNMENTS"
        self.units = ["PPM", "ARBITRARY UNITS", None]
        self.symbols = ["X", "Y", "A"]
        self.formats = ["%f", "%f", "<%s>"]

        self.outputparams = True
        self.grouped = True
        self.forcequote = True


    def get_column(self, i):
        return [row[i] for row in self.data]

    def get_format(self):
        sym = "(%s)"%("".join(self.symbols))
        return sym

    def get_params(self):
        result = {}

        for i in range(len(self.units)):
            
            sym = self.symbols[i]
            unit = self.units[i]

            if unit is not None:
                result[sym + "UNITS"] = unit

        result["NPOINTS"] = str(self.npts)

        return result

    def write(self):

        result = [ ]

        if self.outputparams:
            params = self.get_params()
            result.append(write_dic(params))
            
        result.append(write_line(self.dataclass, self.get_format()))

        for tup in self.data:

            line = []

            for fmt, item in zip(self.formats, tup):
                try:
                    line.append(fmt%item)
                except:
                    line.append("?")

            line = ", ".join(line)
            if self.grouped:
                line = "(" + line + ")"
            result.append(line)

        return "\n".join(result)


class PeakTableData(PeakAssignmentsData):

    """
    PEAK TABLE data table
    data: is in list of lists, with one group per row
    units: required, but None can be used to suprress XUNITS, FIRSTX, etc

    functions the same as PEAK ASSIGNMENTS with different columns

    method write() prints a JCAMP formatted string with the relevant LDRs
    """

    def __init__(self, data):

        self.data = data
        self.npts = len(data)
        self.dim = len(data[0])

        self.dataclass = "PEAK TABLE"
        self.units = ["PPM", "ARBITRARY UNITS"]
        self.symbols = ["X", "Y"]
        self.formats = ["%f", "%f"]

        self.outputparams = True
        self.grouped = False
        self.forcequote = True


           
class XYPointsData():

    """
    XYPOINTS data table
    data: two column x,y np.ndarray

    method write() prints a JCAMP formatted string with the relevant LDRs
    """

    def __init__(self, data):

        self.data = data
        self.npts = len(data)
        self.dim = len(data[0])

        self.dataclass = "XYPOINTS"

        self.units = ["PPM", "ARBITRARY UNITS"]
        self.symbols = ["X","Y"]
        self.formats = ["%10.4f", "%10.4f"]


    def get_column(self, i):
        return self.data[:, i]

    def get_format(self):
        sym = "(%s..%s)"%("".join(self.symbols), "".join(self.symbols))
        return sym

    def get_params(self):
        result = {}

        for i in range(len(self.units)):          
            unit = self.units[i]
            sym = self.symbols[i]
            result[sym + "UNITS"] = unit

        for i in range(len(self.symbols)):          
            sym = self.symbols[i]
            data = self.get_column(i)
            result["FIRST" + sym] = data[0]
            result["LAST" + sym] = data[-1]
            result["MIN" + sym] = min(data)
            result["MAX" + sym] = max(data)

        result["NPOINTS"] = str(self.npts)

        return result

    def write(self):

        result = [ ]

        params = self.get_params()
        result.append(write_dic(params))

        result.append(write_line(self.dataclass, self.get_format()))
        result.append(encode.xy_to_xypoints(*self.data.T, xfmt=self.formats[0], yfmt=self.formats[1], width=80))

        return "\n".join(result)



class XYData():

    """
    XYDATA data table
    data: two column x,y np.ndarray

    self.factors: if != 1.0, denotes that the data in self.data has been scaled
    scale_data(), unscale_data() can be used to set scaling/factors before writing
    attempts to scale the x axis to integer values, and the y axis to integer values
    between +/-32767

    method write() prints a JCAMP formatted string with the relevant LDRs
    """

    def __init__(self, data):

        self.data = data
        self.npts = len(data)
        self.dim = len(data[0])
        self.factors = [1.0] * self.dim

        self.dataclass = "XYDATA"

        self.units = ["PPM", "ARBITRARY UNITS"]
        self.symbols = ["X","Y"]
        self.formats = ["%10.6f", "%10.6f"]

        self.ntuples = False
        self.compression = "DIF"

    def get_column(self, i):
        return self.data[:, i]

    def get_format(self):
        sym = "(%s++(%s..%s))"%(self.symbols[0], self.symbols[1], self.symbols[1])
        if self.ntuples:
            sym += ", %s"%self.dataclass
        return sym

    def get_params(self):
        result = {}

        for i in range(len(self.units)):          
            unit = self.units[i]
            sym = self.symbols[i]
            result[sym + "UNITS"] = unit

        for i in range(len(self.symbols)):          
            sym = self.symbols[i]
            data = self.get_column(i)
            result["FIRST" + sym] = data[0]
            result["LAST" + sym] = data[-1]
            result["MIN" + sym] = min(data)
            result["MAX" + sym] = max(data)

        for i in range(len(self.factors)):          
            sym = self.symbols[i]
            fac = self.factors[i]
            result[sym + "FACTOR"] = fac

        result["NPOINTS"] = str(self.npts)

        return result

    def write(self):

        result = [ ]

        if not self.ntuples:
            params = self.get_params()
            result.append(write_dic(params))

        if self.ntuples:
            result.append(write_line("DATA TABLE", self.get_format()))
        else:
            result.append(write_line(self.dataclass, self.get_format()))

        result.append(encode.xy_to_xydata(*self.data.T, form=self.compression, xfmt=self.formats[0], yfmt=self.formats[1]))

        return "\n".join(result)

    def scale_x(self):
        x = self.data[:, 0]
        test = float(x[0]) - int(x[0])
        diff = x[1] - x[0]
        if np.isclose(test, 0) and (diff != 1.0):
            self.formats[0] = "%10i"
            self.factors[0] = diff
            self.data[:, 0] /= diff
        elif diff == 1:
            self.formats[-3] = "%10i"

    def scale_y(self, maxval=32767):
        absmax = np.max(np.abs(self.data[:, 1]))
        scale = absmax/maxval
        self.formats[1] = "%10i"
        self.factors[1] = scale
        self.data[:, 1] /= scale

    def scale_data(self):
        self.scale_x()
        self.scale_y()

    def unscale_data(self):
        for i, f in enumerate(self.factors):
            if f != 1.0:
                self.data[:, i] *= f
                self.factors[i] = 1.0
                self.formats[i] = "%10.6f"

    @classmethod
    def fromblock(cls, data):
        """
        creates an instance of this class from a dictionary returned from 
        parse.parse_jcamp()
        """
        if "XYDATA" in data:
            key = "XYDATA"
        else:
            raise ValueError("XYDATA not found")
        x = np.linspace(float(data["FIRSTX"][0]), float(data["LASTX"][0]), int(data["NPOINTS"][0]))
        y = decode.xydata_to_y(data["XYDATA"])
        d = cls(np.column_stack((x,y)))
        d.factors[1] = float(data["YFACTOR"][0])
        d.units[0] = data["XUNITS"][0]
        d.units[1] = data["YUNITS"][0]
        return d

class NTuplesGeneric():

    """
    NTUPLES data object for arbitrary multidimensional data
    part of ver 6.00 draft spec 
    not known to be used
    no examples other than draft spec
    2D NMR imlementations are other classes
    """

    def __init__(self, data):
        raise NotImplementedError()


class NTuples1DFIDData():

    """
    NTUPLES data table for 1D NMR complex FIDs
    assumes that the data is output in NTUPLES/XYDATA format

    data: 1D complex ndarray. real-only data will have zeros in the imaginary part
    limits: a tuple of (first, last) time points in seconds

    self.factors: if != 1.0, denotes that the data in self.data has been scaled
    scale_data(), unscale_data() can be used to set scaling/factors before writing
    attempts to scale the x axis to integer values, and the y axis to integer values
    between +/-32767

    method write() prints a JCAMP formatted string with the relevant LDRs
    """
    
    def __init__(self, data, limits=[]):

        self.data = data
        self.npts = data.shape
        self.dim = data.ndim

        if len(limits) != 2:
            raise ValueError('require x axis limits=(first, last)')
        self.ranges = limits

        self.factors = [1.0] * 4

        self.datatype = "NMR FID"
        self.dataclass = "XYDATA"

        self.labels = ["TIME","FID/REAL","FID/IMAG", "PAGE NUMBER"]
        self.units = ["SECONDS","ARBITRARY UNITS","ARBITRARY UNITS",""]
        self.symbols =  ["X","R","I","N"]
        self.types = ["INDEPENDENT","DEPENDENT","DEPENDENT","PAGE"]
        self.formats = ["%10.6f","%10.6f","%10.6f","%10.6f"]
        self.fstring = ["AFFN","ASDF","ASDF","AFFN"]
        self.nucleus = ["1H"]

        self.compression = "DIF"

    def get_format(self):
        sym = "(%s++(%s..%s)), %s"%(self.symbols[0], self.symbols[1], self.symbols[1], self.dataclass)
        return sym

    def get_params(self):

        result = {}

        result["VAR_NAME"] = ", ".join(self.labels)
        result["SYMBOL"] = ", ".join(self.symbols)
        result["VAR_TYPE"] = ", ".join(self.types)
        result["VAR_FORM"] = ", ".join(self.fstring)
        result["UNITS"] = ", ".join(self.units)
       
        result["VAR_DIM"] = list(self.data.shape)
        result["VAR_DIM"] += [self.data.shape[-1]] * 2
        result["VAR_DIM"] += [2]
        result["VAR_DIM"] = ", ".join(map(str,result["VAR_DIM"]))

        result["FIRST"] =[self.ranges[0]*self.factors[0], self.data.real[0]*self.factors[1],self.data.imag[0]*self.factors[2],1]
        result["LAST"] = [self.ranges[1]*self.factors[0], self.data.real[-1]*self.factors[1],self.data.imag[-1]*self.factors[2],2]
        result["MIN"] = [min(self.ranges)*self.factors[0], np.min(self.data.real)*self.factors[1],np.min(self.data.imag)*self.factors[2],1]
        result["MAX"] = [max(self.ranges)*self.factors[0], np.max(self.data.real)*self.factors[1],np.max(self.data.imag)*self.factors[2],2]
        for label in ["FIRST", "LAST", "MIN", "MAX"]:
            result[label] = ", ".join(map(str,result[label]))

        result["FACTOR"] = ", ".join(map(str,self.factors))

        return result


    def write(self):

        result = [ ]

        result.append(write_line("NTUPLES", self.datatype))

        params = self.get_params()
        result.append(write_dic(params))
        for p in range(2):
            if p == 0:
                result.append(write_line("PAGE", "%s=%s"%("N",1)))
                x = np.linspace(*self.ranges, self.data.size)
                y = self.data.real
                xydata = XYData(np.column_stack((x,y)))
                xydata.ntuples = True
                xydata.symbols[1] = "R"
                xydata.formats = [self.formats[0], self.formats[1]]
                xydata.compression = self.compression
                result.append(xydata.write())
            if p == 1:
                result.append(write_line("PAGE", "%s=%s"%("N",2)))
                x = np.linspace(*self.ranges, self.data.size)
                y = self.data.imag
                xydata = XYData(np.column_stack((x,y)))
                xydata.ntuples = True
                xydata.symbols[1] = "I"
                xydata.formats = [self.formats[0], self.formats[2]]
                xydata.compression = self.compression
                result.append(xydata.write())

        result.append(write_line("END NTUPLES", self.datatype))

        return "\n".join(result)

    def scale_x(self):
        x = np.linspace(*self.ranges, self.data.size)
        test = float(x[0]) - int(x[0])
        diff = x[1] - x[0]
        if np.isclose(test, 0) and (diff != 1.0):
            self.factors[0] = diff
            self.ranges = tuple(n/diff for n in self.ranges)
            self.formats[0] = "%10i"
        elif diff == 1:
            self.formats[-3] = "%10i"

    def scale_y(self, maxval=32767):
        absmax = max(np.max(np.abs(self.data.real)), np.max(np.abs(self.data.imag)))
        scale = absmax/maxval
        self.factors[1] = self.factors[2] = scale
        self.data /= scale
        self.formats[1] = "%10i"
        self.formats[2] = "%10i"

    def scale_data(self):
        self.scale_x()
        self.scale_y()

    def unscale_data(self):
        self.ranges = tuple(n*self.factors[0] for n in self.ranges)
        self.formats[0] = ["%10.6f"]
        self.formats[1] = ["%10.6f"]
        self.formats[2] = ["%10.6f"]
        self.data.real *= self.factors[1]
        self.data.imag *= self.factors[2]

    @classmethod
    def fromblock(cls, data):
        """
        creates an instance of this class from a dictionary returned from 
        parse.parse_jcamp()
        """

        cpxdata = []
        if "PAGES" in data:
            pages = data["PAGES"]
            npages = len(pages)
            for i,page in enumerate(pages):
                if "DATA TABLE" not in page:
                    raise ValueError("DATA TABLE not found")
                else:
                    #print("parsing PAGE %i/%i"%(i+1, npages), end='\r', file=sys.stderr)
                    cpxdata.append(decode.xydata_to_y(page["DATA TABLE"]))
            #print("", file=sys.stderr)
        else:
            raise ValueError("PAGES not found")

        #if real data make complex??
        if len(cpxdata)==1:
            cpxdata.append(np.zeros(cpxdata[0].size))

        first = data["FIRST"][0].split(",")[0].strip()
        last = data["LAST"][0].split(",")[0].strip()
        npt = data["VAR_DIM"][0].split(",")[0].strip()
        x = np.linspace(float(first), float(last), int(npt))
        y = np.array(cpxdata[0]) + 1j*np.array(cpxdata[1])

        try:
            y = bruker.remove_digital_filter(data, y)
        except:
            pass

        d = cls(y, (float(first), float(last)))
        d.nucleus[0] = data[".OBSERVE NUCLEUS"][0]
        f = data["FACTOR"][0].split(",")
        d.factors[1] = float(f[1].strip())
        d.factors[2] = float(f[2].strip())
        u = data["UNITS"][0].split(",")
        d.units[0] = u[0].strip()


        return d

    @classmethod
    def from_nmrglue(cls, udic, data):
        """
        creates an instance of this class from an nmrglue format udic and array
        """
        if udic['ndim'] != 1: 
            raise ValueError('data is not 1D')

        if not udic[0]['time']:
            raise ValueError('data is not time domain')

        if udic[0]['sw'] != 999.99:
            delta = 1 / udic[0]['sw'] * (2 if udic[0]['complex'] else 1)
        else:
            delta = 1

        c = cls(data, (0.0, delta*(data.size-1)))

        c.nucleus[0] = udic[0]['label']
        return c


    def to_nmrglue(self, obs, refpt=None, refppm=None):
        """
        converts data to nmrglue format udic and array
        udic 'car' requires parameters outside this block and not changed here
        """

        #TODO: 'obs' should probably be moved out

        udic = blank_udic(1)

        left = self.ranges[0]*self.factors[0]
        right = self.ranges[1]*self.factors[0]
        delta = (right - left)/(self.data.size-1)
        isreal = np.all(self.data.imag == 0)

        udic[0]['label'] = self.nucleus[0].replace("^", "")
        udic[0]['size'] = self.data.size
        udic[0]['obs'] = obs
        udic[0]['sw'] = 1 / abs(delta) / (2 if isreal else 1)
        #udic[0]['sw'] = delta * self.data.size

        return udic, self.data




class NTuplesNDFIDData():

    """
    NTUPLES data table for nD NMR complex FID
    Assumes NTUPLES/XYDATA output
    Currently only 2D supported

    data: nD complex ndarray (only 2D supported) 
    limits: a list of tuples, one for each dimension, of (first, last) time point, in seconds
    """

    def __init__(self, data, limits=[], ndim=None, shape=None):

        self.data = data
        self.npts = shape if shape else list(data.shape)
        self.dim = ndim if ndim else int(data.ndim)
        self.ranges = limits

        if len(self.ranges) != self.dim:
            raise ValueError('limits and data dim do not match')

        self.factors = [1.0] * int(self.dim + 2)

        self.datatype = "nD NMR FID"
        self.dataclass = "XYDATA"

        self.labels = ["TIME%i"%(i+1) for i in range(self.dim)]+["FID/REAL","FID/IMAG"]
        self.units = ["SECONDS"]*self.dim+["ARBITRARY UNITS","ARBITRARY UNITS"]
        self.symbols =  ["T%i"%(i+1) for i in range(self.dim)]+["R","I"]
        self.types = ["INDEPENDENT"]*self.dim+["DEPENDENT","DEPENDENT"]
        self.formats = ["%10.6f"]*self.dim+["%10.6f","%10.6f"]
        self.fstring = ["AFFN"]*self.dim+["ASDF","ASDF"]
        self.nucleus = ["1H"]*self.dim

        self.compression = "DIF"

    def get_format(self):
        sym = "(%s++(%s..%s)), %s"%(self.symbols[0], self.symbols[1], self.symbols[1], self.dataclass)
        return sym

    def get_params(self):

        result = {}

        result["VAR_NAME"] = ", ".join(self.labels)
        result["SYMBOL"] = ", ".join(self.symbols)
        result[".NUCLEUS"] = ", ".join(self.nucleus)
        result["VAR_TYPE"] = ", ".join(self.types)
        result["VAR_FORM"] = ", ".join(self.fstring)
        result["UNITS"] = ", ".join(self.units)
       
        result["VAR_DIM"] = list(self.npts)
        result["VAR_DIM"] += [self.data.shape[-1]] * 2
        result["VAR_DIM"] = ", ".join(map(str,result["VAR_DIM"]))

        result["FIRST"] =[self.ranges[i][0]*self.factors[i] for i in range(self.dim)]+[self.data.real.reshape(-1)[0]*self.factors[-2],self.data.imag.reshape(-1)[0]*self.factors[-1]]
        result["LAST"] = [self.ranges[i][1]*self.factors[i] for i in range(self.dim)]+[self.data.real.reshape(-1)[-1]*self.factors[-2],self.data.imag.reshape(-1)[-1]*self.factors[-1]]
        result["MIN"] = [min(self.ranges[i])*self.factors[i] for i in range(self.dim)]+[np.min(self.data.real)*self.factors[-2],np.min(self.data.imag)*self.factors[-1]]
        result["MAX"] = [max(self.ranges[i])*self.factors[i] for i in range(self.dim)]+[np.max(self.data.real)*self.factors[-2],np.max(self.data.imag)*self.factors[-1]]
        for label in ["FIRST", "LAST", "MIN", "MAX"]:
            result[label] = ", ".join(map(str,result[label]))

        result["FACTOR"] = ", ".join(map(str,self.factors))

        return result


    def write(self):

        result = [ ]

        result.append(write_line("NTUPLES", self.datatype))

        params = self.get_params()
        result.append(write_dic(params))

        grid = [np.linspace(tup[0], tup[1], size) for tup,size in zip(self.ranges, self.data.shape)]
        
        for index in np.ndindex(*self.data.shape[:-1]):

            vals = [axis[idx]*fac for idx,axis,fac in zip(index, grid, self.factors)]
            pageidxs = ["%s=%s"%(lab,val) for lab,val in zip(self.symbols, vals)]

            x = grid[-1]
            y = self.data[index]
            first = vals + [x[0]*self.factors[-3], y.real[0]*self.factors[-2], y.imag[0]*self.factors[-1]]

            for p in range(2):
                if p == 0:
                    xydata = XYData(np.column_stack((x,y.real)))
                    xydata.ntuples = True
                    xydata.symbols[0] = self.symbols[-3]
                    xydata.symbols[1] = "R"
                    xydata.formats = [self.formats[-3], self.formats[-2]]
                    xydata.compression = self.compression
                    result.append(write_line("PAGE", ", ".join(pageidxs)))
                    result.append(write_line("FIRST", ", ".join(map(str, first))))
                    result.append(xydata.write())
                if p == 1:
                    xydata = XYData(np.column_stack((x,y.imag)))
                    xydata.ntuples = True
                    xydata.symbols[0] = self.symbols[-3]
                    xydata.symbols[1] = "I"
                    xydata.formats = [self.formats[-3], self.formats[-1]]
                    xydata.compression = self.compression
                    result.append(write_line("PAGE", ", ".join(pageidxs)))
                    result.append(write_line("FIRST", ", ".join(map(str, first))))
                    result.append(xydata.write())

        result.append(write_line("END NTUPLES", self.datatype))

        return "\n".join(result)

    def scale_x(self):
        #only the last axis needs scaling
        x = np.linspace(*self.ranges[-1], self.data.shape[-1])
        test = float(x[0]) - int(x[0])
        diff = x[1] - x[0]

        if np.isclose(test, 0) and (diff != 1.0):
            self.formats[-3] = "%10i"
            self.factors[-3] = diff
            self.ranges[-1] = tuple(n/diff for n in self.ranges[-1])
        elif diff == 1:
            self.formats[-3] = "%10i"

    def scale_y(self, maxval=32767):
        absmax = max(np.max(np.abs(self.data.real)), np.max(np.abs(self.data.imag)))
        scale = absmax/maxval
        self.factors[-1] = self.factors[-2] = scale
        self.data /= scale
        self.formats[-1] = "%10i"
        self.formats[-2] = "%10i"

    def scale_data(self):
        self.scale_x()
        self.scale_y()

    def unscale_data(self):
        self.ranges[-1] = tuple(n*self.factors[-3] for n in self.ranges[-1])
        self.data.real *= self.factors[-2]
        self.data.imag *= self.factors[-1]
        self.formats[-1] = "%10.6f"
        self.formats[-2] = "%10.6f"
        self.formats[-3] = "%10.6f"

    @classmethod
    def fromblock(cls, data):
        ndim = int(data["NUM DIM"][0])

        xarr = [[],] * ndim
        cpxdata = []

        if "PAGES" in data:
            pages = data["PAGES"]
            npages = len(pages)
            for i, page in enumerate(pages):
                if "DATA TABLE" not in page:
                    raise ValueError("DATA TABLE not found")
                else:
                    #print("parsing PAGE %i/%i\r"%(i+1, npages), end='\r')
                    page_var = page["PAGE"][0]
                    page_var = page_var.split(",")
                    page_var = [kv.split("=") for kv in page_var]
                    for x, p in zip(xarr, page_var):
                        x.append(float(p[1]))
                    cpxdata.append(decode.xydata_to_y(page["DATA TABLE"]))
            #print()
        else:
            raise ValueError("PAGES not found")

        y = np.array(cpxdata)

        iscpx = False
        for item in data["VAR_NAME"][0].split(","):
            if "IMAG" in item:
                iscpx = True
                y = y[0::2] + 1j*y[1::2]
                break

        try:
            print("DEBUG FILTER", y.shape)
            y = bruker.remove_digital_filter(data, y)
            size_after_filter = y.shape[-1]
            print("DEBUG FILTER", y.shape)
        except:
            pass

        first = data["FIRST"][0].split(",")[:ndim]
        first = [float(s.strip()) for s in first if s.strip()]

        last = data["LAST"][0].split(",")[:ndim]
        last = [float(s.strip()) for s in last if s.strip()]

        npt = data["VAR_DIM"][0].split(",")[:ndim]
        npt = [int(s.strip()) for s in npt]
        try:
            npt[-1] = size_after_filter
        except:
            pass

        d = cls(y.reshape(tuple(npt)), list(zip(first, last)))

        nuc = data[".NUCLEUS"][0].split(",")
        d.nucleus[:] = [s.strip() for s in nuc]

        fac = data["FACTOR"][0].split(",")
        d.factors[:] = [float(f.strip()) for f in fac]
        for i, f in enumerate(d.factors[:-2]):
            d.ranges[i] = (d.ranges[i][0]/f,d.ranges[i][1]/f)
            

        u = data["UNITS"][0].split(",")
        d.units[:] = [s.strip() for s in u]
        
        return d

    def to_nmrglue(self):
        udic = blank_udic(self.dim)
        data = self.data
        return udic, data


class NTuplesNDSpectrumData():

    """
    NTUPLES data table
    for nD NMR spectra
    data: nD real ndarray
    limits: a list of tuples, one for each dimension, of (first, last) time point, in seconds
    """

    #NTUPLES for nD real spectrum
    #Time input as [(start, stop) for T1, (start,stop) for T2, ...]
    #self.ranges describe the *current* ranges of the data with scaling by FACTOR
    #but jcamp parameters (outside the actual DATA TABLE) are without scaling

    def __init__(self, data, limits=[]):

        self.data = data.real
        self.npts = data.shape
        self.dim = data.ndim

        if len(limits) != self.dim:
            raise ValueError('limits and data dim do not match')
        self.ranges = limits

        self.factors = [1.0] * int(self.dim + 1)

        self.datatype = "nD NMR SPECTRUM"
        self.dataclass = "NTUPLES"
        self.subclass = "XYDATA"

        self.labels = ["FREQUENCY%i"%(i+1) for i in range(self.dim)]+["SPECTRUM"]
        self.units = ["PPM"]*self.dim+["ARBITRARY UNITS"]
        self.symbols =  ["F%i"%(i+1) for i in range(self.dim)]+["Y"]
        self.types = ["INDEPENDENT"]*self.dim+["DEPENDENT"]
        self.formats = ["%10.4f"]*self.dim+["%10i"]
        self.fstring = ["AFFN"]*self.dim+["ASDF"]
        self.nucleus = ["1H"]*self.dim

        self.compression = "DIF"

    @classmethod
    def fromblock(cls, data):
        ndim = int(data["NUM DIM"][0])

        xarr = [[],] * ndim
        cpxdata = []

        if "PAGES" in data:
            pages = data["PAGES"]
            npages = len(pages)
            for i, page in enumerate(pages):
                if "DATA TABLE" not in page:
                    raise ValueError("DATA TABLE not found")
                else:
                    #print("parsing PAGE %i/%i\r"%(i+1, npages), end='\r')
                    page_var = page["PAGE"][0]
                    page_var = page_var.split(",")
                    page_var = [kv.split("=") for kv in page_var]
                    for x, p in zip(xarr, page_var):
                        x.append(float(p[1]))
                    cpxdata.append(decode.xydata_to_y(page["DATA TABLE"]))
            #print()
        else:
            raise ValueError("PAGES not found")

        y = np.array(cpxdata)


        first = data["FIRST"][0].split(",")[:ndim]
        first = [float(s.strip()) for s in first if s.strip()]

        last = data["LAST"][0].split(",")[:ndim]
        last = [float(s.strip()) for s in last if s.strip()]

        npt = data["VAR_DIM"][0].split(",")[:ndim]
        npt = [int(s.strip()) for s in npt]

        #TODO: hypercomplex may need adjustment of size?
        if np.prod(npt) != y.size:
            raise ValueError("shape and number of data points inconsistent")

        d = cls(y.reshape(tuple(npt)), list(zip(first, last)))

        nuc = data[".NUCLEUS"][0].split(",")
        d.nucleus[:] = [s.strip() for s in nuc]

        fac = data["FACTOR"][0].split(",")
        d.factors[:] = [float(f.strip()) for f in fac]
        for i, f in enumerate(d.factors[:-1]):
            d.ranges[i] = (d.ranges[i][0]/f, d.ranges[i][1]/f)

        u = data["UNITS"][0].split(",")
        d.units[:] = [s.strip() for s in u]

        return d


    def get_format(self):
        sym = "(%s++(%s..%s)), %s"%(self.symbols[0], self.symbols[1], self.symbols[1], self.subclass)
        return sym

    def get_params(self):

        result = {}

        result["VAR_NAME"] = ", ".join(self.labels)
        result["SYMBOL"] = ", ".join(self.symbols)
        result[".NUCLEUS"] = ", ".join(self.nucleus)
        result["VAR_TYPE"] = ", ".join(self.types)
        result["VAR_FORM"] = ", ".join(self.fstring)
        result["UNITS"] = ", ".join(self.units)
       
        result["VAR_DIM"] = list(self.data.shape)
        result["VAR_DIM"] += [self.data.shape[-1]]
        result["VAR_DIM"] = ", ".join(map(str,result["VAR_DIM"]))

        result["FIRST"] =[self.ranges[i][0]*self.factors[i] for i in range(self.dim)]+[self.data.real.reshape(-1)[0]*self.factors[-1]]
        result["LAST"] = [self.ranges[i][1]*self.factors[i] for i in range(self.dim)]+[self.data.real.reshape(-1)[-1]*self.factors[-1]]
        result["MIN"] = [min(self.ranges[i])*self.factors[i] for i in range(self.dim)]+[np.min(self.data.real)*self.factors[-1]]
        result["MAX"] = [max(self.ranges[i])*self.factors[i] for i in range(self.dim)]+[np.max(self.data.real)*self.factors[-1]]
        for label in ["FIRST", "LAST", "MIN", "MAX"]:
            result[label] = ", ".join(map(str,result[label]))

        result["FACTOR"] = ", ".join(map(str,self.factors))

        return result


    def write(self):

        result = [ ]

        result.append(write_line("NTUPLES", self.datatype))

        params = self.get_params()
        result.append(write_dic(params))

        grid = [np.linspace(tup[0], tup[1], size) for tup,size in zip(self.ranges, self.data.shape)]
        
        for index in np.ndindex(*self.data.shape[:-1]):

            vals = [axis[idx]*fac for idx,axis,fac in zip(index, grid, self.factors)]
            pageidxs = ["%s=%s"%(lab,val) for lab,val in zip(self.symbols, vals)]

            x = grid[-1]
            y = self.data[index]
            first = vals + [x[0]*self.factors[-2], y.real[0]*self.factors[-1]]

            xydata = XYData(np.column_stack((x,y.real)))
            xydata.ntuples = True
            xydata.symbols[0] = self.symbols[-2]
            xydata.formats = [self.formats[-2], self.formats[-1]]
            xydata.compression = self.compression
            result.append(write_line("PAGE", ", ".join(pageidxs)))
            result.append(write_line("FIRST", ", ".join(map(str, first))))
            result.append(xydata.write())

        result.append(write_line("END NTUPLES", self.datatype))

        return "\n".join(result)

    def scale_x(self):
        #only the last axis needs scaling
        x = np.linspace(*self.ranges[-1], self.data.shape[-1])
        test = float(x[0]) - int(x[0])
        diff = x[1] - x[0]
        if np.isclose(test, 0) and (diff != 1.0):
            self.formats[-2] = "%10i"
            self.factors[-2] = diff
            self.ranges[-1] = tuple(n/diff for n in self.ranges[-1])
        elif diff == 1:
            self.formats[-3] = "%10i"

    def scale_y(self, maxval=32767):
        absmax = max(np.max(np.abs(self.data.real)), np.max(np.abs(self.data.imag)))
        scale = absmax/maxval
        self.factors[-1] = scale
        self.data /= scale
        self.formats[-1] = "%10i"

    def scale_data(self):
        self.scale_x()
        self.scale_y()

    def unscale_data(self):
        self.ranges[-1] = tuple(n*self.factors[-2] for n in self.ranges[-1])
        self.data *= self.factors[-1]
        self.formats[-1] = "%10i"
        self.formats[-2] = "%10i"

    def to_nmrglue(self):
        udic = blank_udic(self.dim)
        data = self.data
        return udic, data


class MolData():

    """
    contains RDKit mol object for JCAMP-CS
    """

    def __init__(self, mol=None):
        self.data = mol

    def write(self):
        result = jcampcs.mol_to_cs(self.data)
        return write_dic(result)
        

class Block():

    """
    base class for JCAMP
    JCAMP files consist of one block (simple) or a list of blocks grouped by a LINK block (compound)
    """

    def __init__(self):

        self.header  = {} #usually required, appear at top
        self.notes = {} #data specific
        self.data = None #class instance with write()
        self.footer = {"END":""}

    #these methods fill in data from parse.parse_jcamp()
    #but only if the keys match
    def update_header(self, dic):
        for k in dic:
            #skip these keys: should be auto-incremented
            if k in ("BLOCKS", "BLOCK_ID"): 
                continue 
            if k in self.header:
                self.header[k] = "\n".join(dic[k])

    def update_notes(self, dic):
        for k in dic:
            if k in self.notes:
                self.notes[k] = "\n".join(dic[k])
            elif k.startswith("$"): #append user-defined records from file
                self.notes[k] = "\n".join(dic[k])

    #extract and format data
    def update_data(self, dic):
        return

    #input from parse.parse_jcamp()
    @classmethod
    def from_parsed(cls, dic):
        jdx = cls()
        jdx.update_header(dic)
        jdx.update_notes(dic)
        jdx.update_data(dic)
        return jdx

    #input from mol/array data
    @classmethod
    def from_data(cls, datacls, *args, **kwargs):
        jdx = cls()
        jdx.data = datacls(*args, **kwargs)
        return jdx

    #takes a data instance
    def set_data(self, data):
        self.data = data
        self.header["DATA CLASS"] = data.dataclass

    #gets the underlying data array/mol etc
    def get_data(self):
        return self.data.data


    def write_data(self):
        if self.data:
            text = self.data.write()
            if text:
                return text

    def set_num_dim(self):
        try:
            if self.data.datatype.startswith("nD NMR"):
                self.header["NUM DIM"] = data.ndim
        except:
            pass

    def write(self):
        result = []
        if self.header:
            text = write_dic(self.header)
            if text:
                result.append(text)
        if self.notes:
            text = write_dic(self.notes)
            if text:
                result.append(text)
        if self.data:
            text = self.write_data()
            if text:
                result.append(text)
        if self.footer:
            text = write_dic(self.footer)
            if text:
                result.append(text)
        return "\n".join(result)



class JcampCS(Block):

    """
    JCAMP-CS for molecular structures
    """

    def __init__(self):
        super().__init__()

        self.header = { "TITLE":"Moleucle",
                        "JCAMP-CS":"3.7",
                        "ORIGIN":"UNKNOWN",
                        "OWNER":"UNKNOWN",
                        "DATE":DateTime.date(),
                        "TIME":DateTime.time(),
                        "BLOCK_ID":None,
                        "CROSS REFERENCE":None,
                        }

        self.notes = {  "CLASS":None,
                        "SPECTROMETER/DATA SYSTEM":None,
                        "INSTRUMENT PARAMETERS":None,

                        "SAMPLE DESCRIPTION":None,
                        "IUPAC NAME":None, #version >= 5.01
                        "CAS NAME":None,
                        "CAS REGISTRY NO":None,
                        "NAMES":None,
                        #"MOLFORM":None, part of mol data
                        "WISWESSER":None,
                        "BEILSTEIN LAWSON NO":None,
                        "MP":None,
                        "BP":None,
                        "REFRACTIVE INDEX":None,
                        "DENSITY":None,
                        "MW":None,
                        "CONCENTRATIONS":None,

                        "SAMPLING PROCEDURE":None,
                        "STATE":None,
                        "PATH LENGTH":None,
                        "PRESSURE":None,
                        "TEMPERATURE":None,
                        "DATA PROCESSING":None,

                        #for FT IR spectra?
                        "ALIAS":None,
                        "ZPD":None,
                        }


        #self.data = MolData(mol)




class JcampDX(Block):

    """
    base JCAMP-DX for spectral data
    """

    def __init__(self):
        super().__init__()

        self.header = { "TITLE":"Spectrum",
                        "JCAMP-DX":"4.24",
                        "DATA TYPE":None,
                        "DATA CLASS":None, #version >= 5.00
                        "NUM DIM":None, #version >= 6.00, for multi-dimensional NTUPLES data
                        "BLOCKS":None, #LINK block
                        "BLOCK_ID":None,
                        "ORIGIN":"UNKNOWN",
                        "OWNER":"UNKNOWN",
                        "DATE":DateTime.date(),
                        "TIME":DateTime.time(),
                        "LONGDATE":None, #version >= 5.01
                        "AUDIT":None, #version >=5.01
                        "SOURCE REFERENCE":None,
                        "CROSS REFERENCE":None,
                        }

        self.notes = {  "CLASS":None,
                        "SPECTROMETER/DATA SYSTEM":None,
                        "INSTRUMENT PARAMETERS":None,

                        "SAMPLE DESCRIPTION":None,
                        "IUPAC NAME":None, #version >= 5.01
                        "CAS NAME":None,
                        "CAS REGISTRY NO":None,
                        "NAMES":None,
                        "MOLFORM":None,
                        "WISWESSER":None,
                        "BEILSTEIN LAWSON NO":None,
                        "MP":None,
                        "BP":None,
                        "REFRACTIVE INDEX":None,
                        "DENSITY":None,
                        "MW":None,
                        "CONCENTRATIONS":None,

                        "SAMPLING PROCEDURE":None,
                        "STATE":None,
                        "PATH LENGTH":None,
                        "PRESSURE":None,
                        "TEMPERATURE":None,
                        "DATA PROCESSING":None,

                        #for FT IR spectra?
                        "ALIAS":None,
                        "ZPD":None,
                        }

        self.data = None

class CompoundJcampDX(Block):

    """
    JCAMP-DX for compound files (contains a list of Blocks)
    """

    def __init__(self):
        super().__init__()
        self.header = { "TITLE":"Compound JCAMP file",
                        "JCAMP-DX":"4.24",
                        "DATA TYPE":"LINK",
                        "BLOCKS":0, #LINK block
                        "ORIGIN":"UNKNOWN",
                        "OWNER":"UNKNOWN",
                        }
        self.data = []

    def write_data(self):
        if self.data:
            result = []
            for data in self.data:
                if data:
                    text = data.write()
                    if text:
                        result.append(text)
            return "\n".join(result)

    def add_block(self, block):
        index = self.header["BLOCKS"] + 1
        block.header["BLOCK_ID"] = index
        self.header["BLOCKS"] = index
        self.data.append(block)

    def link_blocks(self, i, j):
        i_block = self.data[i-1]
        j_block = self.data[j-1]

        if "JCAMP-CS" in i_block.header: i_type = "STRUCTURE"
        else: i_type = i_block.header["DATA TYPE"]
        if "JCAMP-CS" in j_block.header: j_type = "STRUCTURE"
        else: j_type = j_block.header["DATA TYPE"]

        i_str = "%s:BLOCK_ID=%i"%(i_type, i)
        j_str = "%s:BLOCK_ID=%i"%(j_type, j)

        if i_block.header["CROSS REFERENCE"] is None: 
            i_block.header["CROSS REFERENCE"] = j_str
        else:
            i_block.header["CROSS REFERENCE"] += "\n" + j_str
        if j_block.header["CROSS REFERENCE"] is None: 
            j_block.header["CROSS REFERENCE"] = i_str
        else:
            j_block.header["CROSS REFERENCE"] += "\n" + i_str


        

class JcampDXNMR(JcampDX):

    """
    base JCAMP-DX block for NMR
    contains the NMR specific parameters
    """

    def __init__(self):
        super().__init__()
        self.header.update({"JCAMP-DX":5.01,
                            "LONGDATE":DateTime.longdate(),
                            })

        self.notes.update({ ".OBSERVE FREQUENCY":"UNKNOWN", #MHz, required
                            ".OBSERVE NUCLEUS":"UNKNOWN", #required
                            ".SOLVENT REFERENCE":"UNKNOWN", #ppm of reference peak, required (only if not TMS?)
                            ".SOLVENT NAME":None, #solvent details
                            ".SHIFT REFERENCE":None,    #(INTERNAL/EXTERNAL, compound name, ref pt, ppm @ ref pt)
                                                        #for direct dimension only? should other dim be ref'd indirectly?
                                                        #can be used to reference spectrum if available
                                                        #can be calcuated from Bruker OFFSET or SR=SF-BF
                                                        #for Magritek, $REFERENCE_POINT may be more accurate
                                                        #Varian: rfp, rfl, sw
                            ".DELAY":None,  #(RD, ID), required for FID
                                            # in Bruker and Magritek files, 
                                            # this appears to be the delay to switch on the reciever
                                            # in Magritek, ID = 10000 us probably ignored
                            ".ACQUISITION MODE":None, #SIMULTANEOUS, SEQUENTIAL, SINGLE, required for FID
                            ".ACQUISITION SCHEME":None, #version >= 6.00, for 2D FID, NOT PHASE SENSITIVE, STATES, TPPI, STATES-TPPI
                            ".FIELD":None, #field strength in tesla
                            ".DECOUPLER":None,
                            ".FILTER WIDTH":None, 
                            ".ACQUISITION TIME":None,
                            ".ZERO FILL":None,
                            ".AVERAGES":None,
                            ".DIGITISER RES":None,
                            ".SPINNING RATE":None,
                            ".MAS FREQUENCY":None,
                            ".PHASE 0":None,
                            ".PHASE 1":None,
                            ".MIN INTENSITY":None,
                            ".MAX INTENSITY":None,
                            ".OBSERVE 90":None,
                            ".PULSE SEQUENCE":None,
                            ".COUPLING CONSTANTS":None, #need CROSS REFERENCE to molecule
                            ".RELAXATION TIMES":None,
                            })

    def get_solvent_from_nmrglue(self, dic, udic):
        #dic is from initial nmrglue parsing

        solvent = None

        if "$SOLVENT" in dic: #bruker
            solvent = unquote_string(dic["$SOLVENT"][0].strip())
        elif 'procpar' in dic: #varian
            solvent = dic['procpar']['solvent']['values'][0]

        return solvent

    def get_ref_from_nmrglue(self, dic, udic):
        #get left edges

        left = []
        for dim in range(udic['ndim']):

            revdim = dic['ndim'] - dim

            #varian: not ideal since dimensions can be skipped

            if revdim > 1:
                acqfile = "acqu%is"%(revdim)
                varpar = {'rfp':'rfp%i'%(revdim), 'rfl':'rfl%i'%(revdim), 'sw':'sw%i'%(revdim)}
            else:
                acqfile = "acqus"
                varpar = {'rfp':'rfp','rfl':'rfl', 'sw':'sw'}

            if udic[dim]['car'] != 999.99 and udic[dim]['sw'] != 999.99:
                hz = udic[dim]['car'] + udic[dim]['sw']/2
            elif acqfile in dic and "$OFFSET" in dic[acqfile]: #bruker
                hz = float(dic[acqfile]["$OFFSET"][0])
            elif "procpar" in dic: #varian
                rfp = dic['procpar'][varpar['rfp']]['values'][0]
                rfl = dic['procpar'][varpar['rfl']]['values'][0]
                sw = dic['procpar'][varpar['sw']]['values'][0]
                hz = sw+rfl-rfp

            left.append(hz / udic[dim]['obs'])

        return left




class NMRSpectrum(JcampDXNMR):
    
    #1D spectrum
    #assume XYDATA (non-complex data)

    def __init__(self):
        super().__init__()

        self.header.update({"DATA TYPE":"NMR SPECTRUM",
                            "DATA CLASS":"XYDATA",
                            })

    @classmethod
    def from_nmrglue_1d(cls, udic, data, dic={}):

        car  = udic[0]['car']
        sw  = udic[0]['sw']
        obs = udic[0]['obs']
        nuc = udic[0]['label']
        size = data.size
        delta = sw/size
        left = (car - sw/2)/obs
        right = left + delta * (size-1)
        x = np.linspace(left, right, size)
        y = data

        spec = cls()
        spec.data = XYData(np.column_stack((x,y)))

        spec.notes[".OBSERVE FREQUENCY"] = obs
        spec.notes[".OBSERVE NUCLEUS"] = nuc

        solv = spec.get_solvent_from_nmrglue(self, dic, udic)
        leftppm = spec.get_ref_from_nmrglue(self, dic, udic)[-1]

        if not np.isclose(left / obs, leftppm):
            left = leftppm * obs
            right = left + delta * (size-1)
            spec.data.data[:,0] = np.linspace(left, right, size)

        spec.notes[".SOLVENT NAME"] = solvent
        spec.notes[".SOLVENT REFERENCE"] = leftppm
        spec.notes[".SHIFT REFERENCE"] = ('INTERNAL','<%s>'%sovlent,1,leftppm)

        return spec

    def to_nmrglue_1d(self, refpt=None, refppm=None):

        if self.header['DATA CLASS'] == "XYDATA":

            #may not be referenced correctly unless .SHIFT REFERNCE defined

            units = self.data.units[0]
            size = self.data.data.shape[0]
            nuc = self.notes['.OBSERVE NUCLEUS'].replace("^","")
            obs = float(self.notes['.OBSERVE FREQUENCY'])
            first = self.data.data[0,0] * self.data.factors[0]
            last = self.data.data[-1,0] * self.data.factors[0]
            delta = (last - first) / (size - 1)

            if units == "PPM":
                #ppm to hz
                first = first * obs
                last = last * obs
                delta = delta * obs
            elif units == "HZ":
                pass
            else:
                raise ValueError('unknown units')

            udic = blank_udic(1)

            udic['solvent'] = self.notes[".SOLVENT NAME"].lower() if self.notes[".SOLVENT NAME"] else ""
            udic['format'] = 'jcamp'
            udic['temp'] = float(self.notes["TEMPERATURE"] or 0)
            udic['pulseseq'] = ""


            udic[0]['complex'] = False
            udic[0]['time'] = False
            udic[0]['freq'] = True

            udic[0]['obs'] = obs
            udic[0]['label'] = nuc
            udic[0]['size'] = size

            udic[0]['sw'] = abs(delta) * size
            udic[0]['car'] = first + delta * (size // 2)

            data = self.data.data[:,1]

            ref = self.notes['.SHIFT REFERENCE']
            off = self.notes['$OFFSET'] if '$OFFSET' in self.notes else None
            o1 = self.notes['$O1'] if '$O1' in self.notes else None

            if ref is not None:
                if type(ref) is str: #comes from parser
                    #print("SHIFT REFERENCE found for F2")
                    if ref.startswith("("):
                        ref = ref.strip()[1:-1]
                    ref = ref.split(",")
                    pt = float(ref[2].strip()) #1
                    val = float(ref[3].strip()) * obs #10.7*700.32 = 7500
                    #recalculate carrier
                    cardist = (udic[0]['size']//2+1) - pt #points from ref to car #2048
                    car = val + delta * cardist #hz at car given ref #1@7500 -> 2048@????
                    udic[0]['car'] = car
            elif (off is not None) and (off.strip() != "4.7") and abs(float(off.strip())) < 1e8:
                if type(off) is str:
                    #print("Bruker OFFSET found for F2")
                    off = float(off.strip()) * obs
                    car = off + delta * (size // 2)
                    udic[0]['car'] = car
                    if o1 is not None:
                        car = float(o1)
                        diff = abs(car - udic[0]['car'])
                        if diff > udic[0]['sw']/10:
                            #print('using O1 instead')
                            udic[0]['car'] = car
            elif o1 is not None:
                #print('O1 found')
                car = float(o1)
                udic[0]['car'] = car
                
            elif nuc is not None: #use some default value
                try:
                    car = NucTable.get_nuc(nuc)['default_car'] * obs
                    udic[0]['car'] = car
                    #print('referencing not found, using a default for nucleus')
                except:
                    pass

        if self.header['DATA CLASS'] == "NTUPLES":
            #NTUPLES for complex 1d or general 2d
            raise NotImplementedError()

        return udic, data


    def to_nmrglue_2d(self, refpt=None, refppm=None):

        if self.header['DATA CLASS'] != "NTUPLES":
            raise ValueError('2d NMR spectra should be NTUPLES')

        udic, data = self.data.to_nmrglue()
        print("DEBUG", "INSIDE TONMRGLUE SPECTRUM")

        udic['solvent'] = self.notes[".SOLVENT NAME"].lower() if self.notes[".SOLVENT NAME"] else ""
        udic['format'] = 'jcamp'
        udic['temp'] = float(self.notes["TEMPERATURE"] or 0)
        udic['pulseseq'] = ""


        #update direct dim
        lastdim = udic['ndim']-1

        units = self.data.units[1]
        size = self.data.data.shape[1]
        nuc = self.notes['.OBSERVE NUCLEUS'].replace("^","")
        obs = float(self.notes['.OBSERVE FREQUENCY'])
        first = self.data.ranges[-1][0] * self.data.factors[1]
        last = self.data.ranges[-1][1] * self.data.factors[1]
        delta = (last - first) / (size - 1)

        if units == "PPM":
            #ppm to hz
            first = first * obs
            last = last * obs
            delta = delta * obs
        elif units == "HZ":
            pass
        else:
            raise ValueError('unknown units')


        udic[lastdim]['complex'] = False
        udic[lastdim]['time'] = False
        udic[lastdim]['freq'] = True

        udic[lastdim]['obs'] = obs
        udic[lastdim]['label'] = nuc
        udic[lastdim]['size'] = size

        udic[lastdim]['sw'] = abs(delta) * size
        udic[lastdim]['car'] = first + delta * (size // 2)

        ref = self.notes['.SHIFT REFERENCE']
        off = self.notes['$OFFSET'] if '$OFFSET' in self.notes else None
        o1 = self.notes['$O1'] if '$O1' in self.notes else None

        if ref is not None:
            if type(ref) is str: #comes from parser
                #print('SHIFT REFERENCE in F2 found')
                if ref.startswith("("):
                    ref = ref.strip()[1:-1]
                ref = ref.split(",")
                pt = float(ref[2].strip())
                val = float(ref[3].strip()) * obs
                #recalculate carrier
                cardist = (udic[lastdim]['size']//2+1) - pt #points from ref to car
                car = val + delta * cardist #hz at car given ref
                udic[lastdim]['car'] = car
        elif (off is not None) and (off.strip() != "4.7") and abs(float(off.strip())) < 1e8:
            if type(off) is str:
                #print('Bruker OFFSET in F2 found')
                off = float(off.strip()) * obs
                car = off + delta * (size // 2)
                udic[lastdim]['car'] = car
                if o1 is not None:
                    car = float(o1)
                    diff = abs(car - udic[lastdim]['car'])
                    if diff > udic[lastdim]['sw']/10:
                        #print('using O1 instead')
                        udic[lastdim]['car'] = car
        elif o1 is not None:
            #print('O1 found')
            car = float(o1)
            udic[0]['car'] = car
        elif nuc is not None: #use some default value
            try:
                car = NucTable.get_nuc(nuc)['default_car'] * obs
                udic[lastdim]['car'] = car
                #print('referencing in F2 not found, using a default value for nucleus')
            except:
                pass

        #update indirect dim
        #in general, must assume first and last in hz/ppm set correctly
        #if bruker data: could potentially go through procNs parameters
        #todo: handle jres

        f1units = self.data.units[0]
        f1size = self.data.data.shape[0]
        f1nuc = self.data.nucleus[0].replace("^","")
        f1first = self.data.ranges[0][0] * self.data.factors[0]
        f1last = self.data.ranges[0][1] * self.data.factors[0]
        f1delta = (f1last - f1first) / (f1size - 1)
        f1obs = obs * NucTable.get_nuc(f1nuc)['gamma'] / NucTable.get_nuc(nuc)['gamma'] 

        if f1units == "PPM":
            #ppm to hz
            f1first = f1first * f1obs
            f1last = f1last * f1obs
            f1delta = f1delta * f1obs
        elif f1units == "HZ":
            pass
        else:
            raise ValueError('unknown units')

        #bruker keys parsed so that OFFSET -> F1_OFFSET
        off = self.notes['$F1_OFFSET'] if '$F1_OFFSET' in self.notes else None
        o2 = self.notes['$O2'] if '$O2' in self.notes else None

        if off is not None:
            if type(off) is str:
                #print('Bruker OFFSET in F1 found')
                off = float(off.strip()) * f1obs
                car = off + f1delta * (f1size // 2)
                udic[0]['car'] = car
                if o2 is not None:
                    car = float(o2)
                    diff = abs(car - udic[0]['car'])
                    if diff > udic[0]['sw']/10:
                        #print('using O2 instead')
                        udic[0]['car'] = car
        elif o2 is not None:
            #print('O2 found')
            car = float(o2)
            udic[0]['car'] = car
        elif f1nuc is not None:
            try:
                car = NucTable.get_nuc(f1nuc)['default_car'] * f1obs
                udic[0]['car'] = car
                #print('referencing in F1 not found, using a default value for nucleus')
            except:
                pass
            pass

        udic[0]['complex'] = False
        udic[0]['time'] = False
        udic[0]['freq'] = True

        udic[0]['obs'] = f1obs
        udic[0]['label'] = f1nuc
        udic[0]['size'] = f1size

        udic[0]['sw'] = abs(f1delta) * f1size
        udic[0]['car'] = f1first + f1delta * (f1size // 2)



        return udic, data

class NMRFid(JcampDXNMR):
    
    #1D spectrum
    #assumes NTUPLES/XYDATA

    def __init__(self):
        super().__init__()

        self.header.update({"DATA TYPE":"NMR FID",
                            "DATA CLASS":"NTUPLES",
                            })

        #required for FID
        self.notes.update({ ".DELAY":(0.0, 0.0),
                            ".ACQUISITION MODE":"SIMULTANEOUS",
                            })
                            
    @classmethod
    def from_nmrglue_1d(cls, udic, data):
        spec = cls()
        spec.notes[".OBSERVE FREQUENCY"] = udic[0]['obs']
        spec.notes[".OBSERVE NUCLEUS"] = udic[0]['label']
        spec.data = NTuples1DFIDData.from_nmrglue(udic, data)

        solv = spec.get_solvent_from_nmrglue(self, dic, udic)
        left = spec.get_ref_from_nmrglue(self, dic, udic)[-1]

        spec.notes[".SOLVENT NAME"] = solvent
        spec.notes[".SOLVENT REFERENCE"] = left
        spec.notes[".SHIFT REFERENCE"] = ('INTERNAL','<%s>',1,left)

        return spec

    def to_nmrglue_1d(self):

        if self.header['DATA CLASS'] == "NTUPLES":

            udic, data = self.data.to_nmrglue(float(self.notes[".OBSERVE FREQUENCY"]))

            udic['solvent'] = self.notes[".SOLVENT NAME"].lower() if self.notes[".SOLVENT NAME"] else ""
            udic['format'] = 'jcamp'
            udic['temp'] = float(self.notes["TEMPERATURE"] or 0)
            udic['pulseseq'] = ""

            obs = float(self.notes[".OBSERVE FREQUENCY"])
            delta = (self.data.ranges[1] - self.data.ranges[0])/(len(self.data.data)-1)
            off = self.notes['$O1'] if '$O1' in self.notes else None
            nuc = self.notes['.OBSERVE NUCLEUS'].replace("^","")

            #OFFSET IS **NOT** saved for FID in TOPSPIN!!!
            #O1 or SFO1 could be used as a best guess for bruker jcamp
            #magritek, SF might might be used?
            if off is not None:
                #print('O1 in F2 found')
                car = float(off)
                udic[0]['car'] = car

            elif nuc is not None: #use some default value
                try:
                    car = NucTable.get_nuc(nuc)['default_car'] * obs
                    udic[0]['car'] = car
                    #print('referencing in F2 not found, using a default value')
                except:
                    pass

        return udic, data


    def to_nmrglue_2d(self, refpt=None, refppm=None):

        if self.header['DATA CLASS'] != "NTUPLES":
            raise ValueError('2d NMR spectra should be NTUPLES')
        
        udic, data = self.data.to_nmrglue()

        udic['solvent'] = self.notes[".SOLVENT NAME"].lower() if self.notes[".SOLVENT NAME"] else ""
        udic['format'] = 'jcamp'
        udic['temp'] = float(self.notes["TEMPERATURE"] or 0)
        udic['pulseseq'] = ""

        #update direct dim
        lastdim = udic['ndim']-1

        units = self.data.units[1]
        size = self.data.data.shape[1]
        nuc = self.notes['.OBSERVE NUCLEUS'].replace("^","")
        obs = float(self.notes['.OBSERVE FREQUENCY'])
        first = self.data.ranges[-1][0] * self.data.factors[1]
        last = self.data.ranges[-1][1] * self.data.factors[1]
        delta = (last - first) / (size - 1)
        sw = 1/delta

        if units != "SECONDS":
            raise ValueError('unknown units')


        udic[lastdim]['complex'] = True
        udic[lastdim]['time'] = True
        udic[lastdim]['freq'] = False

        udic[lastdim]['obs'] = obs
        udic[lastdim]['label'] = nuc
        udic[lastdim]['size'] = size

        udic[lastdim]['sw'] = sw
        udic[lastdim]['car'] = sw/2


        #OFFSET IS **NOT** saved for FID in TOPSPIN!!!
        #O1 or SFO1 could be used as a best guess for bruker jcamp
        #magritek, SF might might be used?
        off = self.notes['$O1'] if '$O1' in self.notes else None
        if off is not None and off != "4.7":
            #print('O1 in F2 found')
            car = float(off)
            udic[lastdim]['car'] = car
        elif nuc is not None: #use some default value
            try:
                car = NucTable.get_nuc(nuc)['default_car'] * obs
                udic[lastdim]['car'] = car
                #print('referencing in F2 not found, using a default value')
            except:
                pass

        #update indirect dim
        #in general, must assume first and last in hz/ppm set correctly
        #if bruker data: could potentially go through acquNs parameters

        f1units = self.data.units[0]
        f1size = self.data.data.shape[0]
        f1nuc = self.data.nucleus[0].replace("^","")
        f1first = self.data.ranges[0][0] * self.data.factors[0]
        f1last = self.data.ranges[0][1] * self.data.factors[0]
        f1delta = (f1last - f1first) / (f1size - 1)
        f1sw = 1/f1delta
        f1obs = obs * NucTable.get_nuc(f1nuc)['gamma'] / NucTable.get_nuc(nuc)['gamma'] 

        if units != "SECONDS":
            raise ValueError('unknown units')

        udic[0]['encoding'] = 'states'
        udic[0]['complex'] = True

        udic[0]['time'] = True
        udic[0]['freq'] = False

        udic[0]['obs'] = f1obs
        udic[0]['label'] = f1nuc
        udic[0]['size'] = f1size

        udic[0]['sw'] = f1sw
        udic[0]['car'] = f1sw / 2

        if ".ACQUISITION SCHEME" in self.notes:
            acq = self.notes[".ACQUISITION SCHEME"].upper()
            if "ECHO" in acq:
                udic[0]['encoding'] = 'echo-antiecho'
                udic[0]["complex"] = True
            elif "STATES-TPPI" in acq:
                udic[0]["encoding"] = "states-tppi"
                udic[0]["complex"] = True
            elif "STATES" in acq:
                pass #default
            elif "TPPI" in acq:
                udic[0]["encoding"] = "tppi"
                udic[0]["complex"] = False
                f1sw = f1sw/2
                udic[0]['sw'] = udic[0]['sw']/2
                udic[0]['car'] = udic[0]['car']/2
            elif "NOT" in acq:
                udic[0]["encoding"] = "magnitude"
                udic[0]["complex"] = False
                f1sw = f1sw/2
                udic[0]['sw'] = udic[0]['sw']/2
                udic[0]['car'] = udic[0]['car']/2

        #OFFSET IS **NOT** saved for FID in TOPSPIN!!!
        #O1 or SFO1 could be used as a best guess for bruker jcamp
        #magritek, SF might might be used?
        off = self.notes['$O2'] if '$O2' in self.notes else None
        if off is not None and abs(float(off)) < 1e7:
            #print('O2 in F1 found')
            car = float(off)
            udic[0]['car'] = car
        if f1nuc is not None: #use some default value
            try:
                car = NucTable.get_nuc(f1nuc)['default_car'] * f1obs
                udic[0]['car'] = car
                #print('referencing in F1 not found, using a default value')
            except:
                pass

        return udic, data


class NMRPeakAssignments(JcampDXNMR):

    def __init__(self):
        super().__init__()

        self.header.update({"DATA TYPE":"NMR PEAK ASSIGNMENTS",
                            "DATA CLASS":"PEAK ASSIGNMENTS",
                            })

        raise NotImplementedError

class NMRPeakTable(JcampDXNMR):

    def __init__(self):
        super().__init__()

        self.header.update({"DATA TYPE":"NMR PEAK TABLE",
                            "DATA CLASS":"PEAK TABLE",
                            })

        raise NotImplementedError


class FileParser():

    """
    function FileParser.parse_jcamp(filename) returns a Jcamp instance
    """

    datatypes = {"LINK":CompoundJcampDX,
                "INFRARED SPECTRUM":None, 
                "RAMAN SPECTRUM":None,
                "INFRARED PEAK TABLE":None, 
                "INFRARED INTERFEROGRAM":None, 
                "INFRARED TRANSFORMED SPECTRUM":None,
                "MASS SPECTRUM":None,
                "CONTINUOUS MASS SPECTRUM":None,
                "ION MOBILITY SPECTRUM":None,
                "IMS PEAK TABLE":None,
                "IMS PEAK ASSIGNMENTS":None,
                "NMR FID":NMRFid, #1D/NTUPLES/XYDATA, nD/NTUPLES/XYDATA, 
                "NMR SPECTRUM":NMRSpectrum, #1D/NTUPLES/XYDATA, 2D/NTUPLES/XYDATA
                "NMR PEAK TABLE":None, #TODO?
                "NMR PEAK ASSIGNMENTS":NMRPeakAssignments, #PEAKASSIGNMENTS:TODO
                "EMR MEASUREMENT":None,
                "EMR SIMULATION":None,
                "CHROMATOGRAPHY":None,
                "GAS CHROMATOGRAPHY/MASS SPECTROMETRY":None,
                "LIQUID CHROMATOGRAPHY/MASS SPECTROMETRY":None,
                }

    dataclasses = { "XYDATA":XYData, #done (generic)
                    "XYPOINTS":None, #No NMR examples?
                    "NTUPLES":None, #No (version >= 6.0)
                    "PEAK TABLE":PeakTableData, #TODO
                    "PEAK ASSIGNMENTS":PeakAssignmentsData, #TODO
                    }

    ntuplesclasses = {"NMR FID":NTuples1DFIDData,
                      "NMR SPECTRUM":None, #This would be complex data
                      "ND NMR FID":NTuplesNDFIDData,
                      "ND NMR SPECTRUM":NTuplesNDSpectrumData,
                        }   
    @staticmethod
    def parse_jcamp(filename):
        return parse.parse_jcamp(filename)

    @classmethod
    def create_block(cls, data):

        if "JCAMP-CS" in data:
            #print('found structure data')
            jdx = JcampCS()
            jdx.update_header(data)
            jdx.update_notes(data)
            jdx.data = cls.create_data(data)
            return jdx

        elif ("JCAMP-DX" in data) and ("DATA TYPE") in data:
            datatype = data["DATA TYPE"][0].upper()
            #print('found data type = %s'%datatype)
            jdx = cls.datatypes[datatype]()
            jdx.update_header(data)
            jdx.update_notes(data)
            jdx.data = cls.create_data(data)
            return jdx

        else:
            raise ValueError('unknown block format')

    @classmethod
    def create_data(cls, data):

        if "JCAMP-CS" in data:
            #print('found data = structure')
            mol = jcampcs.cs_to_mol(data)
            d = MolData(mol)
            return d

        #version >= 5.0 have DATA CLASS
        elif ("JCAMP-DX" in data) and ("DATA CLASS") in data:

            c = data["DATA CLASS"][0].upper()
            #print('found data class =', c)

            #sepearte parsers for each NTUPLES
            if c == "NTUPLES":
                c = data["NTUPLES"][0].upper()
                if c in cls.ntuplesclasses:
                    #print('==>', c)
                    d = cls.ntuplesclasses[c].fromblock(data)
                    return d
                else:
                    print('skipping unknown format %s'%c, file=sys.stderr)

            #generic parser for non NTUPLES
            else:
                if c in cls.dataclasses:
                    d = cls.dataclasses[c].fromblock(data)
                    return d
                else:
                    print('skipping unknown format %s'%c, file=sys.stderr)

        #older jcamp may not have DATA CLASS
        else:
            c = None
            for key in cls.dataclasses:
                if key in data:
                    c = key
                    d = cls.dataclasses[c].fromblock(data)
                    return d

        #otherwise...
        print('skipping unknown data block TITLE=%s'%data["TITLE"], file=sys.stderr)


    #input data from cls.parse_jcamp()
    @classmethod
    def create_jcamp(cls, data):

        if len(data["SUBBLOCKS"]) == 0:
            #print('found empty jcamp file')
            return None

        elif len(data["SUBBLOCKS"]) > 1:
            #print('found concatenated jcamp file')
            #create cpd object and add_blocks...
            jdx = CompoundJcampDX()
            for subblock in block["SUBBLOCKS"]:
                jdx.add_block(cls.create_block(subblock))

        else:

            block = data["SUBBLOCKS"][0]

            if ("DATA TYPE" in block) and (block["DATA TYPE"] == ["LINK"]):
                #print('found compound jcamp file')
                #create cpd object and add_blocks...
                jdx = cls.create_block(block)
                for subblock in block["SUBBLOCKS"]:
                    jdx.add_block(cls.create_block(subblock))

            else:
                #print('found simple jcamp file')
                jdx = cls.create_block(block)

        return jdx

    @classmethod
    def read_jcamp(cls, filename):
        data = cls.parse_jcamp(filename)
        jdx = cls.create_jcamp(data)
        return jdx

def plot_2d(data, udic=None, thres=None):

    import matplotlib.pyplot as plt
    import nmrglue as ng

    def noise_std_2d(data, binsize=25):

        #find noise standard deviation by binning into grid

        noise_std = []

        data = data.real
        x, y = data.shape[0]//binsize, data.shape[1]//binsize

        #print("NOISE 2D", data.shape, binsize, x, y)

        for i, j in np.ndindex((x, y)):
            xst, xend = binsize*i, binsize*i+binsize
            yst, yend = binsize*j, binsize*j+binsize
            block = data[xst:xend,yst:yend]
            std = np.std(block)
            noise_std.append(std)

        return np.median(noise_std)


    def contour_levels(data, scale=20, factor=1.1, number=20, 
                        threshold=0, linear=False, show='all'):

        #for matplotlib plotting
        
        _2d_min = np.min(data.real)
        _2d_max = np.max(data.real)

        if threshold is not None:
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


    if udic:
        xaxis = ng.fileiobase.uc_from_udic(udic, 1)
        yaxis = ng.fileiobase.uc_from_udic(udic, 0)

        if udic[1]['time'] == True:
            xaxis = xaxis.sec_scale()
        else:
            xaxis = xaxis.ppm_scale()

        if udic[0]['time'] == True:
            yaxis = yaxis.sec_scale()
        else:
            yaxis = yaxis.ppm_scale()


    if thres is None:
        noise = noise_std_2d(data)
        thres = noise * 5

    if np.all(data > 0):
        thres = thres * 2

    #print("DEBUG 2D PLOT", thres)
    arg = 20, 1.2, 20, thres, False, 'all'
    contours, colors = contour_levels(data, *arg)

    if udic:
        plt.contour(xaxis, yaxis, data, levels=contours, colors=colors, linewidths=0.5)
    else:
        plt.contour(data, levels=contours, colors=colors, linewidths=0.5)

    if udic:
        if udic[1]['time'] == False:
            plt.gca().invert_xaxis()
        if udic[0]['time'] == False:
            plt.gca().invert_yaxis()

    return


def test():

    from rdkit.Chem import AllChem as Chem
    from rdkit.Chem import rdDepictor
    import matplotlib.pyplot as plt
    import nmrglue as ng


    #parse test (NMR FID/1D/NTUPLES/XYDATA)
    #test = "testdata/nmr_fid_60_mag.dx"
    #test = "testdata/TESTFID.DX"
    test = "v3/testdata/700_1d_fid.dx"
    data = FileParser.parse_jcamp(test)
    jdx = FileParser.create_jcamp(data)
    jdx.data.scale_x()
    jdx.data.scale_y()
    #print(jdx.write())
    u,d = jdx.to_nmrglue_1d()
    print(u)
   # xaxis = np.fft.fftshift(np.fft.fftfreq(u[0]['size'], 1/u[0]['sw']))[::-1]
    #if u[0]['car'] != 999.99: 
    #    xaxis += u[0]['car']
    #    xaxis/= u[0]['obs']
    #uc = ng.fileio.fileiobase.uc_from_udic(u)
    #plt.plot(xaxis, np.fft.fftshift(np.fft.fft(d)))
    #plt.plot(d)
    #plt.show()


    """
    #parse test (NMR SPECTRUM/1D/XYDATA)
    #test = "testdata/BRUKDIF.DX"
    test = "testdata/bruk_spec_700.dx"
    data = FileParser.parse_jcamp(test)
    jdx = FileParser.create_jcamp(data)
    jdx.data.scale_x()
    jdx.data.scale_y()
    #print(jdx.write())
    u,d = jdx.to_nmrglue_1d()
    print(u)
    xaxis = np.fft.fftshift(np.fft.fftfreq(u[0]['size'], 1/u[0]['sw']))[::-1]
    if u[0]['car'] != 999.99: 
        xaxis += u[0]['car']
        xaxis/= u[0]['obs']
    plt.plot(xaxis, d)
    plt.show()
    """

    """
    #parse test (NMR SPECTRUM/2D/NTUPLES/XYDATA)
    #test = "testdata/isasspc1.dx"
    test = "testdata/nmr_2d_spec_700_bru.dx"
    data = FileParser.parse_jcamp(test)
    #print(list(data["SUBBLOCKS"][0].keys()))
    #print(data["SUBBLOCKS"][0]['.SHIFT REFERENCE'])
    jdx = FileParser.create_jcamp(data)
    #jdx.data = None
    #print(jdx.write())
    u,d = jdx.to_nmrglue_2d()
    print(u)
    #print(d.shape)
    plot_2d(d, u)
    plt.show()
    """

    """
    #parse test (NMR FID/2D/NTUPLES/XYDATA)
    test = "testdata/isasfid1.dx"
    #test = "testdata/700_2d_fid.dx"
    data = FileParser.parse_jcamp(test)
    #print(list(data["SUBBLOCKS"][0].keys()))
    jdx = FileParser.create_jcamp(data)
    #jdx.data = None
    #jdx.data.scale_x()
    #jdx.data.scale_y()
    #print(jdx.write())

    params = jdx.data.get_params()
    print(write_dic(params))

    u,d = jdx.to_nmrglue_2d()
    print(u)
    """

if __name__ == "__main__": 


    test()

