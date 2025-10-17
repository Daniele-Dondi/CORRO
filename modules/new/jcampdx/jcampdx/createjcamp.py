import os, time, glob, datetime
import numpy as np
from scipy.interpolate import interp1d
import csv
import re
import xml.etree.ElementTree as ET
import rdkit.Chem as Chem
import itertools
import extract_varian


#TODO: perhaps skip blocks with nonexistent file input



SQZ_POS = { "+0":"@",
            "+1":"A",
            "+2":"B",
            "+3":"C",
            "+4":"D",
            "+5":"E",
            "+6":"F",
            "+7":"G",
            "+8":"H",
            "+9":"I",}

SQZ_NEG = { "-0":"@",
            "-1":"a",
            "-2":"b",
            "-3":"c",
            "-4":"d",
            "-5":"e",
            "-6":"f",
            "-7":"g",
            "-8":"h",
            "-9":"i",}


DIF_POS = { "+0":"%",
            "+1":"J",
            "+2":"K",
            "+3":"L",
            "+4":"M",
            "+5":"N",
            "+6":"O",
            "+7":"P",
            "+8":"Q",
            "+9":"R",}

DIF_NEG = { "-0":"%",
            "-1":"j",
            "-2":"k",
            "-3":"l",
            "-4":"m",
            "-5":"n",
            "-6":"o",
            "-7":"p",
            "-8":"q",
            "-9":"r",}

DIF_DUP = { "1":"S",
            "2":"T",
            "3":"U",
            "4":"V",
            "5":"W",
            "6":"X",
            "7":"Y",
            "8":"Z",
            "9":"s",}

frq_scale = {"1H":1,
             "13C":10.7084/42.57638474,
             "15N":4.316/42.57638474,
             "31P":17.235/42.57638474,
             "19F":40.078/42.57638474,
             "2H":6.536,
             }

def read_tsv(inputfile):
    #tab/space separated
    #print('reading as tsv', inputfile, file=sys.stderr)
    try:
        return np.loadtxt(inputfile)
    except:
        return np.loadtxt(inputfile,dtype=str)

def read_csv(inputfile):
    #comma separated
    #print('reading as csv', inputfile, file=sys.stderr)
    try:
        return np.loadtxt(inputfile,delimiter=",")
    except:
        return np.loadtxt(inputfile,delimiter=",",dtype=str)


def read_json(inputfile):
    import json
    #generic json data
    with open(inputfile) as f:
        j = json.load(f)
    return j


def read_json_1d(inputfile):
    import json
    #bayesil/magmet format json
    with open(inputfile) as f:
        j = json.load(f)
    x = j['spectrum_xy']['x']
    y = j['spectrum_xy']['y']
    return np.column_stack((x,y))

def read_json_2d(inputfile):
    import json
    #bayesil/magmet format json
    with open(inputfile) as f:
        j = json.load(f)
    x = j['x']
    y = j['y']
    z = j['z']
    return np.array(x), np.array(y), np.array(z).reshape((len(x), len(y)))

def read_nmrml_spectrum(inputfile):

    #spectrum only (not FID)

    import base64, zlib, re

    matchstr = "\s*<(spectrumDataArray.*?)>(.*)</spectrumDataArray>"
    str1 = "compressed=\"(.*?)\""
    str2 = "encodedLength=\"(.*?)\""
    str3 = "byteFormat=\"(.*?)\""

    x = y = None

    #hmdb nmrml files
    with open(inputfile) as f:

        for line in f:

            match = re.match(matchstr,line)

            if match:

                header = match.group(1)
                data = match.group(2)

                compressed = re.search(str1,header).group(1)
                encodedLength = re.search(str2,header).group(1)
                byteFormat = re.search(str3,header).group(1)

                data = base64.b64decode(data)

                if compressed.lower() == "true":
                    data = zlib.decompress(data)

                dataarr = np.frombuffer(data,byteFormat)
                x, y = dataarr.real, dataarr.imag

    if x is None or y is None:
        raise ValueError('unable to parse NMRML file')

    return np.column_stack((x, y))



class block():

    #use $COMMENTS:comment... to write "$$ comment..." near top of block

    #None: dont write line
    #"": write blank entry
    #convert lists etc to strings before write()

    def __init__(self, form="DX", data_type=None, datafile=None):

        self.block = {}
        self.pages = []
        self.footer = {}

        if form == "CS":

            if data_type is not None and data_class is not None:
                raise ValueError()

            self.block.update({"TITLE":"STRUCTURE",
                               "JCAMP-CS":"3.7",
                               "ORIGIN":"UNKNOWN",
                               "OWNER":"UNKNOWN",
                               "DATE":None, #YY/MM/DD
                               "TIME":None, #HH:MM:SS
                               "BLOCK_ID":None, #for compound files
                               "CROSS REFERENCE":None, #for compound files
                               "$COMMENTS":None,})

            self.footer.update({"END":""})

            return


        if form == "DX" and data_type == "LINK":

            #no END= until end of file

            self.block.update({"TITLE":"LINK BLOCK",
                               "JCAMP-DX":"4.24",
                               "DATA TYPE":"LINK",
                               "ORIGIN":"UNKNOWN",
                               "OWNER":"UNKNOWN",
                               "BLOCKS":None,
                               "$COMMENTS":None,
                               })
            return


        if form == "DX" and data_type != "LINK":


            if data_type not in ("NMR FID", "NMR SPECTRUM", "NMR PEAK TABLE",
                                "NMR PEAK ASSIGNMENTS", "nD NMR SPECTRUM", "nD NMR FID",
                                 "NMR 2D PEAK ASSIGNMENTS", "nD NMR PEAK TABLE"):

                raise ValueError('unknown DATA TYPE')


            self.footer.update({"END":""})

            self.block.update({"TITLE":data_type,
                               "JCAMP-DX":"4.24",
                               "DATA TYPE":data_type,
                               "ORIGIN":"UNKNOWN",
                               "OWNER":"UNKNOWN",
                               "DATA CLASS":None,
                               "BLOCK_ID":None, #for compound files
                               "CROSS REFERENCE":None, #for compound files
                               "DATE":None,
                               "TIME":None,
                               "$COMMENTS":None,})

            self.block.update({"SAMPLE DESCRIPTION":None,
                               "CONCENTRATIONS":None,
                                #for single compound?
                               "NAMES":None,
                               "IUPAC NAME":None,
                               "CAS NAME":None,
                               "CAS REGISTRY NO":None,
                               "MOLFORM":None,
                               "MP":None,
                               "BP":None,
                               "MW":None,
                               })

            self.block.update({"SPECTROMETER/DATA SYSTEM":None, #recommened
                               "INSTRUMENT PARAMETERS":None, #recommened
                               "SAMPLING PROCEDURE":None,
                               "PRESSURE":None,
                               "TEMPERATURE":None,
                               "$PH":None,
                               "DATA PROCESSING":None})



            if data_type and "NMR" in data_type:

                self.block.update({"JCAMP-DX":"5.01"})

                self.block.update({"LONG DATE":None, #5.01 YYYY/MM/DD [HH:MM:SS.SSSS] [±UUUU]
                                   "SOURCE REFERENCE":None, #5.01,
                                   "AUDIT TRAIL":None}) #5.01

###AUDIT TRAIL= $$ (NUMBER, WHEN, WHO, WHERE, WHAT)
#(1, <1998/09/15 12:00 +0000>, <Joe Bloggs>, <London, UK>, <baseline correction, not reversible>)
#(2, <1998/09/16 07:00 -0500>, <Jane Doe>, <New York, USA>, <authorized 1>)

                #required parameters
                self.block.update({".OBSERVE FREQUENCY":"UNKNOWN", #MHz
                                   ".OBSERVE NUCLEUS":"UNKNOWN", #eg "^1H"

                                   ".SOLVENT NAME":None, #5.01, not required, but useful, can be detailed

                                   #for spectra
                                   ".SOLVENT REFERENCE":None, #in ppm, required if solvent used as reference peak, use same value in shift-reference if available
                                   ".SHIFT REFERENCE":None, #optional, but supercedes solvent reference, "INTERNAL/EXTERNAL, CPD NAME, DATA IDX, PPM AT IDX"
                                   "$INDIRECT REFERENCE":None, #used for 2nd dimension?, no clear value

                                   #for fid
                                   ".DELAY":None, #required, preaquisition delay as "(n, n)" in microsseconds
                                   ".ACQUISITION MODE":None,}) #required, either: simultatenous, sequential, single

                self.block.update({"RESOLUTION":None,
                                   "DELTAX":None,
                                   })

                self.block.update({".FIELD":None,
                                   ".DECOUPLER":None,
                                   ".FILTER WIDTH":None,
                                   ".AQUISITION TIME":None,
                                   ".ZERO FILL":None,
                                   ".AVERAGES":None,
                                   ".DIGITISER RES":None,
                                   ".SPINNING RATE":None,
                                   ".PHASE O":None,
                                   ".PHASE 1":None,
                                   ".MIN INTENSITY":None,
                                   ".MAX INTENSITY":None,
                                   ".OBSERVE":None,
                                   ".COUPLING CONSTANTS":None, #eg  = J(A,B)\n 4.5(5,10)\n 7.4(10,15) #perhaps best used with the peak assignment block?
                                   ".RELAXATION TIMES":None,
                                   })

                #new in 5.01
                self.block.update({".PULSE SEQUENCE":None,
                                   ".MAS FREQUENCY":None,
                                   })



            if data_type and "nD NMR" in data_type: #nD NMR  SPECTRUM or nD NMR FID

                self.block.update({"JCAMP-DX":"6.00",
                                    #this should prob be added later
                                    "NUM_DIM":"2",
                                    ".ACQUISITION SCHEME":"NOT PHASE SENSITIVE",
                                    "$GRPDLY":None})
                                    #not phase sens: for magn data or processed spectrum
                                    #states: cos and sin modulated fids, T1: 1R, 1I, 2R, 2I, ...
                                    #tppi: shift spectrum, T1: 1R, 2R, 3R, 4R,...
                                    #states tppi: T1: 1R, 1I, 2R, 2I, ...
                                    #echo antiecho: p and n type fids, T1: 1R, 1I, 2R, 2I,... shuffle 1R=(1R+1I), 1I=(1R-1I)...

                """ Bruker example:
                    ##NTUPLES= nD NMR SPECTRUM
                    ##VAR_NAME=  FREQUENCY1,    FREQUENCY2,      SPECTRUM
                    ##SYMBOL=    F1,            F2,              Y
                    ##.NUCLEUS=  ,              1H
                    ##VAR_TYPE=  INDEPENDENT,   INDEPENDENT,     DEPENDENT
                    ##VAR_FORM=  AFFN,          AFFN,            ASDF
                    ##VAR_DIM=   1024,          1024,            1024
                    ##UNITS=     HZ,            HZ,              ARBITRARY UNITS
                    ##FACTOR=    3.90624762783991, 3.90625,      1
                    ##FIRST=     3800.58361954689, 3996.09375,   4106
                    ##LAST=      -195.50770373334, 0,            7066
                    ##MIN=       -195.50770373334, 0,            0
                    ##MAX=       3800.58361954689, 3996.09375,   370755047
                    ##PAGE= F1=3800.583619547
                    ##FIRST=     3800.58361954689, 3996.09375,   4106
                    ##DATA TABLE= (F2++(Y..Y)), PROFILE"""

            return

    def write(self):
        for k in self.block:
            if self.block[k] is None: continue
            if k == "$COMMENTS" and self.block[k] is not None:
                for line in self.block[k]:
                    print("$$ %s"%(self.block[k]))
            elif k.startswith("$$"):
                if type(block[k]) is list:
                    print("$$%s=%s"%(k, self.block[k][0]))
                    for line in self.block[k][1:]:
                        print("$$ %s"%(self.block[k]))
                else:
                    print("$$%s=%s"%(k, self.block[k]))
            else:
                print("##%s=%s"%(k, self.block[k]))
        for p in self.pages:
            for k in p:
                if p[k] is None: continue
                print("##%s=%s"%(k, p[k]))
        for k in self.footer:
            if self.footer[k] is None: continue
            print("##%s=%s"%(k, self.footer[k]))

    def add_comment(self,comment):
        if self.block["$COMMENTS"] is None: self.block["$COMMENTS"] = []
        self.block["$COMMENTS"].append(comment)

    def add_mol(self, molfile):
        data = make_mol(molfile)
        self.block.update(data)

    def add_1d_spectrum(self, specfile, filetype="csv", compression="DIF", unzipfolder=None):

        if filetype == "csv":
            data = read_csv(specfile)
        if filetype == "tsv":
            data = read_tsv(specfile)
        if filetype == "json":
            data = read_json_1d(specfile)
        if filetype == "bruk":
            if specfile.endswith('.zip'):
                print('zip file found', file=sys.stderr)
                outdir = unzip_bruker_fid(specfile, tmpfolder=unzipfolder)
                if not outdir:
                    print('data not found', file=sys.stderr)
                    return
                specfile = outdir
                print('data found', specfile, file=sys.stderr)
            b, data = make_bruker_1d_spec(specfile)
            self.block.update(b)
        if filetype == "var":
            if specfile.endswith('.zip'):
                print('zip file found', file=sys.stderr)
                outdir = unzip_var_fid(specfile, tmpfolder=unzipfolder)
                if not outdir:
                    print('data not found', file=sys.stderr)
                    return
                specfile = outdir
                print('data found', specfile, file=sys.stderr)
            b, data = make_varian_1d_spec(specfile)
            self.block.update(b)


        self._specdata = data
        xdata = data[:,0]
        ydata = data[:,1]
        mask = (xdata > 5) | (xdata < 4.6)
        mask2 = (xdata > 0.2) | (xdata < -0.2)
        ymax = np.max(ydata[mask & mask2])
        self._specmax = ymax

        b = make_spectrum(data, labels=["X","Y"], units=["PPM","ARBITRARY UNITS"], compression=compression)
        self.block.update(b)

    def add_assignments(self, assignfile,filetype="csv"):
        if filetype == "csv":
            data = read_csv(assignfile)
        if filetype == "tsv":
            data = read_tsv(assignfile)

        b = make_assignments(data, table_format="XMA", labels=["X"], units=["PPM"])
        self.block.update(b)

    def add_2dassignments(self, assignfile, filetype="csv"):
        if filetype == "csv":
            data = parse_2d_peak_list(assignfile)
        else:
            return

        b = make_2dassignments(data)
        self.block.update(b)


    def add_peaktable(self, assignfile,filetype="csv", specmax=None):
        if filetype == "csv":
            data = read_csv(assignfile)
        if filetype == "tsv":
            data = read_tsv(assignfile)
        if filetype == "json":
            data = read_json(assignfile)
            data = json_to_1d_peaktable(data)

        #yscale = specmax

        b = make_peaktable(data, table_format="XY..XY", labels=["X","Y"], units=["PPM","ARBITRARY UNITS"])
        self.block.update(b)

    def add_2dpeaktable(self, assignfile,filetype="json", specmax=None):

        if filetype == "json":
            data = read_json(assignfile)
            data = json_to_peaktable(data)

        #yscale = specmax

        #print("DEBUG", data, file=sys.stderr)

        b, p, f = make_2dpeaktable(data, labels=["X","Y","Z"], units=["PPM","PPM","ARBITRARY UNITS"])
        self.block.update(b)
        self.pages = p
        oldfooter = self.footer
        self.footer = f
        self.footer.update(oldfooter) #put end ntuples before end


    def add_coup_from_assigntable(self, coupfile):
        with open(coupfile) as csvfile:
            reader = csv.reader(csvfile)
            coupdata = [line for line in reader]
        b = make_couptable(coupdata)
        self.block.update(b)

    def add_1d_fid(self, fidfile, filetype="csv", compression="DIF", neg_imag=False, unzipfolder=None):
        if filetype == "csv":
            data = read_csv(fidfile)
        if filetype == "tsv":
            data = read_tsv(fidfile)
        if filetype == "bruk":
            if fidfile.endswith('.zip'):
                print('zip file found', file=sys.stderr)
                outdir = unzip_bruker_fid(fidfile, findpdata=False, tmpfolder=unzipfolder)
                if not outdir:
                    print('data not found', file=sys.stderr)
                    return
                fidfile = outdir
                print('data found', fidfile, file=sys.stderr)
            b, data = read_bruker_1d_fid(fidfile)
            self.block.update(b)

        if filetype == "var":
            if fidfile.endswith('.zip'):
                print('zip file found', file=sys.stderr)
                outdir = unzip_var_fid(fidfile, tmpfolder=unzipfolder)
                if not outdir:
                    print('data not found', file=sys.stderr)
                    return
                fidfile = outdir
                print('data found', fidfile, file=sys.stderr)
            b, data = make_varian_1d_fid(fidfile)
            #print(b)
            self.block.update(b)

        if neg_imag:
            data[:,2] *= -1
        if filetype == "var":
            pass

        b, p, f = make_fid(data, compression=compression)
        self.block.update(b)
        self.pages = p
        oldfooter = self.footer
        self.footer = f
        self.footer.update(oldfooter) #put end ntuples before end

    def add_2dspectrum(self, specfile, filetype, compression="DIF", unzipfolder=None):
        if filetype == 'var':
            if specfile.endswith('.zip'):
                print('zip file found', file=sys.stderr)
                outdir = unzip_var_fid(specfile, tmpfolder=unzipfolder)
                if not outdir:
                    print('data not found', file=sys.stderr)
                    return
                specfile = outdir
                print('data found', specfile, file=sys.stderr)
            b, p, f = make_varian_2d_spec(specfile, compression)

        if filetype == 'bruk':
            if specfile.endswith('.zip'):
                print('zip file found', file=sys.stderr)
                outdir = unzip_bruker_fid(specfile, tmpfolder=unzipfolder)
                if not outdir:
                    print('data not found', file=sys.stderr)
                    return
                specfile = outdir
                print('data found', specfile, file=sys.stderr)
            b, p, f = make_bruker_2d_spec(specfile, compression)
        if filetype == 'json':
            b, p, f = make_2d_spec_json(specfile, compression)

        self.block.update(b)
        self.pages = p
        oldfooter = self.footer
        self.footer = f
        self.footer.update(oldfooter) #put end ntuples before end
        return

    def add_2dfid(self, specfile, filetype, compression="DIF", unzipfolder=None):
        if filetype == 'var':
            if specfile.endswith('.zip'):
                print('zip file found', file=sys.stderr)
                outdir = unzip_var_fid(specfile, tmpfolder=unzipfolder)
                if not outdir:
                    print('data not found', file=sys.stderr)
                    return
                specfile = outdir
                print('data found', specfile, file=sys.stderr)
            b, p, f = make_varian_2d_fid(specfile, compression)
        if filetype == 'bruk':
            if specfile.endswith('.zip'):
                print('zip file found', file=sys.stderr)
                outdir = unzip_bruker_fid(specfile, findpdata=False, tmpfolder=unzipfolder)
                if not outdir:
                    print('data not found', file=sys.stderr)
                    return
                specfile = outdir
                print('data found', specfile, file=sys.stderr)
            b, p, f = make_bruker_2d_fid(specfile, compression)

        self.block.update(b)
        self.pages = p
        oldfooter = self.footer
        self.footer = f
        self.footer.update(oldfooter) #put end ntuples before end
        return

    def set_param(self, param, val):
        if param == "$COMMENTS": self.block[param].append(val)
        else:  self.block[param] = val


def json_to_1d_peaktable(data):

    peaktable = []

    for i in data:
        peak = data[i]
        if float(peak['xlw']) == 0:
            continue

        #emtpy rows to match csv file format
        peakrow = [0, 0, 0, ]
        peakrow.append(float(peak['xpos']))
        peakrow.append(float(peak['int']))
        peaktable.append(peakrow)

    return peaktable


def json_to_peaktable(data):
    """
0:
ypos    7.846505701751855
xpos    139.9819615529459
ylw    0.22559562374783404
xlw    0.3952258765770864
int    595142.2047629794
vol    100956932.84164487
1:
...
    """
    peaktable = [] #x, y, int

    #filter out peaks with lw == 0?

    for i in data:
        peak = data[i]
        if float(peak['xlw']) == 0:
            continue
        if float(peak['ylw']) == 0:
            continue
        peakrow = []
        peakrow.append(float(peak['xpos'])) #indirect
        peakrow.append(float(peak['ypos'])) #direct
        peakrow.append(float(peak['int']))
        peaktable.append(peakrow)

    #print(data, file=sys.stderr)
    #print(peaktable, file=sys.stderr)

    return peaktable

def unzip_bruker_fid(zipfile, findpdata=True, tmpfolder="/tmp/"):

    import shutil

    if tmpfolder is None:
        tmpfolder = os.path.dirname(zipfile)

    rand = str(time.time())
    outdir = os.path.join(tmpfolder, rand)

    print('unzipping to', outdir, file=sys.stderr)


    shutil.unpack_archive(zipfile, outdir, 'zip')

    dircontents = glob.glob(os.path.join(outdir, "**/*"), recursive=True)
    #print(dircontents)

    for filename in dircontents:
        head, tail = os.path.split(filename)

        if findpdata:
            if tail.startswith("2rr"):
                #datadir/fid
                #datadir/pdata/1/1r
                print('procd data found', filename, file=sys.stderr)
                return head

        if not findpdata:
            if tail == "fid" or tail == "ser":
                print('raw data found', filename, file=sys.stderr)
                return head

    return None

def unzip_var_fid(zipfile, tmpfolder="/tmp/"):

    import shutil

    if tmpfolder is None:
        tmpfolder = os.path.dirname(zipfile)

    rand = str(time.time())
    outdir = os.path.join(tmpfolder, rand)

    print('unzipping to', outdir, file=sys.stderr)


    shutil.unpack_archive(zipfile, outdir, 'zip')

    dircontents = glob.glob(os.path.join(outdir, "**/*"), recursive=True)
    #print(dircontents)

    for filename in dircontents:
        head, tail = os.path.split(filename)

        if tail.startswith("procpar"):
            #datadir/fid
            #datadir/pdata/1/1r
            print('procpar found', filename, file=sys.stderr)
            return head


    return None

def make_mol(molfilename, ispath=True):

    block = {}

    block.update({"MOLFORM":"", #formula Cnn Hnn ...
                  "ATOMLIST":"",
                  "BONDLIST":None,
                  "CHARGE":None,
                  "RADICAL:":None,
                  "STEREOCENTER":None,
                  "STEREOPAIR":None,
                  "STEREOMOLECULE":None,
                  "MAX_RASTER":None,
                  "XY_RASTER_FACTOR":None,
                  "XY_RASTER":None,
                  "XYZ_SOURCE":None,
                  "MAX_XYZ":None,
                  "XYZ_FACTOR":None,
                  "XYZ":None,
                  "$MOLFILE":None, #like to acdlabs output
                  "PEAK ASSIGNMENTS":None,
                 })

    from rdkit.Chem import AllChem as Chem

    try:
        if ispath:
            with open(molfilename) as mf:
                molfile = mf.read()
        else:
            molfile = molfilename #file aready read as string

        block["$MOLFILE"] = molfile

        mol = Chem.MolFromMolBlock(molfile, removeHs=False)
        Chem.Kekulize(mol, clearAromaticFlags=True)
    except:
        return {}

    #TODO: separate molecules with "*"?, isotopes?, ^ and /?
    formula = []
    for c in Chem.CalcMolFormula(mol):
        if formula and c.isupper():
            formula.append(" " + c)
        else:
            formula.append(c)
    formula = "".join(formula)

    block['MOLFORM'] = formula

    atomblock = []
    chargeblock = {}
    stereoblock = []

    for a in mol.GetAtoms():

        atomblock.append("%s %s %s"%(a.GetIdx()+1, a.GetSymbol(), a.GetImplicitValence()))

        charge = a.GetFormalCharge()

        if charge:
            if charge > 0:
                charge = "+" + str(charge)
            elif charge < 0:
                charge = str(charge)
            if charge not in chargeblock:
                chargeblock[charge] = []
            chargeblock[charge].append(str(a.GetIdx()+1))

        chiral = a.GetChiralTag()
        if chiral == Chem.ChiralType.CHI_TETRAHEDRAL_CCW:
            stereoblock.append("%s %s 0"%(a.GetIdx()+1, "M"))
        if chiral == Chem.ChiralType.CHI_TETRAHEDRAL_CW:
            stereoblock.append("%s %s 0"%(a.GetIdx()+1, "P"))

    block['ATOMLIST'] = "\n" + "\n".join(atomblock)

    if chargeblock:
        block['CHARGE'] = "\n" + "\n".join([c + " " + " ".join(chargeblock[c]) for c in chargeblock])

    if stereoblock:
        block['STEREOCENTER'] = "\n" + "\n".join(stereoblock)

    bondtypedic = {1:"S",2:"D",3:"T",4:"Q"}
    bondblock = []
    stereobonds = []
    for b in mol.GetBonds():

        bondtype = b.GetBondTypeAsDouble()
        if bondtype in bondtypedic:
            bondtype = bondtypedic[bondtype]
        else:
            bondtype = "A"
        bondblock.append("%s %s %s"%(b.GetBeginAtomIdx()+1, b.GetEndAtomIdx()+1, bondtype))

        stereo = b.GetStereo()

        if stereo != Chem.BondStereo.STEREOANY and  stereo != Chem.BondStereo.STEREONONE:

            if stereo == Chem.BondStereo.STEREOTRANS or stereo == Chem.BondStereo.STEREOE:
                stereo = "M"
            if stereo == Chem.BondStereo.STEREOCIS or stereo == Chem.BondStereo.STEREOZ:
                stereo = "P"

            stereoatoms = [a+1 for a in b.GetStereoAtoms()]
            bondatoms = b.GetBeginAtomIdx()+1, b.GetEndAtomIdx()+1,
            stereoligands = [[n.GetIdx()+1 for n in mol.GetAtomWithIdx(a-1).GetNeighbors()] for a in bondatoms]
            flipstereo = 0
            if stereoatoms[0] != min(stereoligands[0]): flipstereo += 1
            if stereoatoms[1] != min(stereoligands[1]): flipstereo += 1
            if flipstereo%2:
                if stereo == "M": stereo == "P"
                if stereo == "P": stereo == "M"

            stereobonds.append("%s %s %s 0"%(bondatoms[0], bondatoms[1], stereo))

    block['BONDLIST'] = "\n" + "\n".join(bondblock)

    if stereobonds:
        block['STEREOPAIR'] = "\n" + "\n".join(stereobonds)

    return block


def scale_data(data, scale='yauto',maxy=None):

    #value to DIVIDE data by, such that data*scale is the original data

    if scale == 'xauto':
        scale = np.abs(data[1] - data[0])

    if scale == 'yauto':
        if maxy is None: maxy = 32767
        if np.iscomplexobj(data):
            _data = np.concatenate((data.real, data.imag), axis=None)
        else:
            _data = data
        pos = _data[_data > 0]
        neg = _data[_data < 0]
        if pos.size:    pos = np.max(pos)/maxy
        else:           pos = 0
        if neg.size:    neg = np.min(neg)/-maxy
        else:           neg = 0
        scale = max(pos, neg)

    if scale == 0: scale = 1

    data = data / scale

    return data, scale

def get_range(data, scale, dimlabel="", units=None):

    #data is alrady scaled
    #need range for whole data, not for eg each page

    params = {}

    params[dimlabel + "UNITS"] = units

    params["FIRST" + dimlabel] = str(data[0] * scale)
    params["LAST" + dimlabel] = str(data[-1] * scale)

    params["MIN" + dimlabel] = str(np.min(data*scale))
    params["MAX" + dimlabel] = str(np.max(data*scale))

    params[dimlabel + "FACTOR"] = str(scale)

    params["NPOINTS"] = str(len(data))

    return params


def xy_to_dx(x, y,
             xprec=5,yprec=0,
             cols=80,
             form="DIF",
             xsym="X",ysym="Y"):

    #data should already be scaled
    #egx*xscale is the original data
    #prec is output precision

    params = {}

    lines = []
    line = []

    params["XYDATA"] = [ "({0}++({1}..{1})), XYDATA $$ {2}".format(xsym,ysym,form) ] #list to add data lines to later

    tmpx = []
    tmpy = []
    tmpd = []

    for i in range(x.size):

        tmpx.append('{0:0.{1}f}'.format(x[i], xprec))
        tmpy.append('{0:+0.{1}f}'.format(y[i], yprec))

        if i == 0:
            tmpd.append(None)
        else:
            #rounding - diff should reflect scaled, rounded y values
            tmpd.append('{0:+0.{1}f}'.format( float(tmpy[i])-float(tmpy[i-1]), yprec))

        #print(tmpx[-1],tmpy[-1],tmpd[-1])


    if form == "FIX":

        xsize = len('{0:+0.{1}f}'.format(max(np.max(x),-np.min(x)), xprec))
        ysize = len('{0:+0.{1}f}'.format(max(np.max(y),-np.min(y)), yprec))

        tmpsize = 0
        tmpline = []
        i = 0

        while i < x.size:

            #pad with space, x: left align, y: right align
            xi = '{0:<{1}}'.format(tmpx[i],xsize)
            yi = '{0:>{1}}'.format(tmpy[i],ysize)

            if len(tmpline) == 0: #first x,y pair
                tmpline.append(xi)
                tmpline.append(yi)
                tmpsize += len(xi)
                tmpsize += len(yi) + 1 #space before y value

            elif tmpsize + len(yi) + 1 <= cols:
                tmpline.append(yi)
                tmpsize += len(yi) + 1 #space before y value

            else: #if length >= col, clear line and rewind
                lines.append(" ".join(tmpline))
                tmpsize = 0
                tmpline = []
                i -= 1

            i += 1

        if i == x.size: #for last point
            lines.append(" ".join(tmpline))
            tmpsize = 0
            tmpline = []


    if form == "PAC":

        tmpsize = 0
        tmpline = []
        i = 0

        while i < x.size:

            xi = tmpx[i]
            yi = tmpy[i]

            if len(tmpline) == 0: #first x,y pair
                tmpline.append(xi)
                tmpline.append(yi)
                tmpsize += len(xi)
                tmpsize += len(yi)

            elif tmpsize + len(yi) <= cols:
                tmpline.append(yi)
                tmpsize += len(yi)

            else:
                lines.append("".join(tmpline))
                tmpsize = 0
                tmpline = []
                i -= 1

            i += 1

        if i == x.size: #for last point
            lines.append("".join(tmpline))
            tmpsize = 0
            tmpline = []



    if form == "SQZ":

        tmpsize = 0
        tmpline = []
        i = 0

        while i < x.size:

            xi = tmpx[i]
            yi = tmpy[i]

            if   yi[0] == "+": yi = SQZ_POS[yi[:2]] + yi[2:]
            elif yi[0] == "-": yi = SQZ_NEG[yi[:2]] + yi[2:]

            if len(tmpline) == 0: #first x,y pair
                tmpline.append(xi)
                tmpline.append(yi)
                tmpsize += len(xi)
                tmpsize += len(yi)

            elif tmpsize + len(yi) <= cols:
                tmpline.append(yi)
                tmpsize += len(yi)

            else:
                lines.append("".join(tmpline))
                tmpsize = 0
                tmpline = []
                i -= 1

            i += 1

        if i == x.size: #for last point
            lines.append("".join(tmpline))
            tmpsize = 0
            tmpline = []

    if form == "DIF":

        tmpsize = 0
        tmpline = []
        i = 0

        while i < x.size:

            xi = tmpx[i]
            yi = tmpy[i]
            di = tmpd[i]

            if   yi[0] == "+": yi = SQZ_POS[yi[:2]] + yi[2:]
            elif yi[0] == "-": yi = SQZ_NEG[yi[:2]] + yi[2:]

            if i == 0: pass
            elif di[0] == "+": di = DIF_POS[di[:2]] + di[2:]
            elif di[0] == "-": di = DIF_NEG[di[:2]] + di[2:]

            if len(tmpline) == 0: #first x,y pair
                tmpline.append(xi)
                tmpline.append(yi)
                tmpsize += len(xi)
                tmpsize += len(yi)

            elif tmpsize + len(di) <= cols: # use dif after first y per line
                tmpline.append(di)
                tmpsize += len(di)

            else:
                #add line and clear
                lines.append("".join(tmpline))
                tmpsize = 0
                tmpline = []
                #rewind, Y value calc'd from diff of last line used as checkpoint
                #X1 Y1 D2,1 D3,2 ... DN,N-1
                #XN YN ...
                i -= 2

            i += 1

        if i == x.size: #for last point
            lines.append("".join(tmpline))
            tmpsize = 0
            tmpline = []

        lines.append( xi + yi + " $$ checkpoint")


    if form == "DIFDUP":

        tmpsize = 0
        tmpline = []
        i = 0

        todif = lambda n: DIF_DUP[str(n)[0]] + str(n)[1:]
        toline = lambda l: l[0]+"".join([s[2] for s in l[1:]])

        while i < x.size:

            xi = tmpx[i]
            yi = tmpy[i]
            di = tmpd[i]

            #print(xi, yi, di)

            if   yi[0] == "+": yi = SQZ_POS[yi[:2]] + yi[2:]
            elif yi[0] == "-": yi = SQZ_NEG[yi[:2]] + yi[2:]

            if i == 0: pass
            elif di[0] == "+": di = DIF_POS[di[:2]] + di[2:]
            elif di[0] == "-": di = DIF_NEG[di[:2]] + di[2:]

            #print(xi, yi, di, tmpline, tmpsize)

            if len(tmpline) == 0: #first x,y pair, y as list for counting

                tmpline.append(xi)
                tmpsize += len(xi)
                tmpline.append([yi,1,yi]) #y string, count, final string
                tmpsize += len(yi)


            elif len(tmpline) == 2 and yi == tmpline[-1][0] and tmpsize - len(tmpline[-1][2]) + len(yi + todif(tmpline[-1][1]+1)) <= cols: #y value same as prev

                #remove from count first
                tmpsize -= len(tmpline[-1][2])
                tmpline[-1][1] += 1
                tmpline[-1][2] = yi + todif(tmpline[-1][1])
                tmpsize += len(tmpline[-1][2])


            elif len(tmpline) == 2 and yi != tmpline[-1][0] and tmpsize + len(di) <= cols: # y is not the same, start using diff

                tmpline.append([di,1,di]) #y string, count, final string
                tmpsize += len(di)

            elif len(tmpline) > 2 and di == tmpline[-1][0] and tmpsize - len(tmpline[-1][2]) + len(di + todif(tmpline[-1][1]+1)) <= cols: # diff value same as prev

                #remove from count first
                tmpsize -= len(tmpline[-1][2])
                tmpline[-1][1] += 1
                tmpline[-1][2] = di + todif(tmpline[-1][1])
                tmpsize += len(tmpline[-1][2])

            elif len(tmpline) > 2 and di != tmpline[-1][0] and tmpsize + len(di) <= cols: # diff value NOT same as prev diff

                tmpline.append([di,1,di]) #y string, count, final string
                tmpsize += len(di)

            else:
                lines.append(toline(tmpline))
                tmpsize = 0
                tmpline = []
                i -= 2

            i += 1

        if i == x.size: #for last point
            lines.append(toline(tmpline))
            tmpsize = 0
            tmpline = []

        lines.append( xi + yi + " $$ checkpoint")

    params["XYDATA"].extend(lines)
    params["XYDATA"] = "\n".join(params["XYDATA"])

    return params, lines


def make_spectrum(data, labels=["X","Y"], units=["PPM","ARBITRARY UNITS"], compression="DIF"):

    #two columns: x, y

    block = {}

    #data = data.T

    xdata, xscale = scale_data(data[:,0],'xauto')
    ydata, yscale = scale_data(data[:,1],'yauto')

    newblock = get_range(xdata, xscale, dimlabel=labels[0], units=units[0])
    block.update(newblock)
    newblock = get_range(ydata, yscale, dimlabel=labels[1], units=units[1])
    block.update(newblock)

    newblock, _ = xy_to_dx( xdata, ydata,
                            xprec=0, yprec=0,
                            cols=80,
                            form=compression,
                            xsym=labels[0], ysym=labels[1])

    block.update(newblock)

    return block



def make_2dpeaktable(data, labels=["X","Y","Z"], units=["PPM","PPM","ARBITRARY UNITS"]):

    #from table
    #shift1 shift2 intensity

    block = {}
    pages = []
    footer = {}

    block.update({"TEMPERATURE":None,
                  ".ACQUISITION SCHEME":None,
                "NUM_DIM":None,})

    block.update({"DATA CLASS":"NTUPLES"})

    block.update({  "NTUPLES":"2D NMR PEAK TABLE",
                    "VAR_NAME":labels,
                    ".NUCLEUS":["UNKNOWN","UNKNOWN",""], #indirect then observe nuc
                    "SYMBOL":["X","Y","Z"],
                    "VAR_TYPE":["INDEPENDENT","INDEPENDENT","DEPENDENT"],
                    "VAR_FORM":["AFFN","AFFN","AFFN"],
                    "VAR_DIM":[len(data)] * 3, #number of points
                    "UNITS":units,
                    "FIRST":["","",""],
                    "LAST":["","",""],
                    "MIN":["","",""],
                    "MAX":["","",""],
                    "FACTOR":[1, 1, 1],})

    block["FIRST"] = data[0][:3]
    block["LAST"] = data[-1][:3]

    for row in data:

        for i in range(3):

            if (block["MIN"][i] != ""):
                if (row[i] < float(block["MIN"][i])):
                    block["MIN"][i] = row[i]
            else: block["MIN"][i] = row[i]

            if (block["MAX"][i] != ""):
                if (row[i] > float(block["MAX"][i])):
                    block["MAX"][i] = row[i]
            else: block["MAX"][i] = row[i]


    for k in block:
        if type(block[k]) is list:
            block[k] = ",".join(map(str,block[k]))

    page = make_page()
    page["PAGE"]=""
    page["PEAK TABLE"] = ["(%s)"%block["SYMBOL"], ]
    for row in data:
        page["PEAK TABLE"].append(",".join(map(str,row[:3])))
    page["PEAK TABLE"] = "\n".join(page["PEAK TABLE"])
    pages.append(page)

    footer.update({"END NTUPLES":"2D NMR PEAK TABLE"})

    #print("DEBUG", block, file=sys.stderr)
    #print("DEBUG", pages, file=sys.stderr)
    #print("DEBUG", footer, file=sys.stderr)

    return block, pages, footer



def make_2dassignments(data, labels=["1H","13C"], units=["PPM","PPM"]):

    block = {}

    if not data:
        return block

    block["DATA CLASS"] = "2D PEAK ASSIGNMENTS"
    block["NPOINTS"] = str(len(data))

    for dim, label in zip(["X","Y"], labels):
        block[dim + "LABEL"] = label

    for label, unit in zip(["X","Y"], units):
        block[label + "UNITS"] = unit

    block["PEAK ASSIGNMENTS"] = "(XYAB)"


    #print(data)
    for pk_id in data:

        row = data[pk_id]

        row[0] = str(row[0])
        row[1] = str(row[1])
        row[2] = "<%s>"%(row[2])
        row[3] = "<%s>"%(row[3])

        block["PEAK ASSIGNMENTS"] += "\n(%s)"%(", ".join(row))

    return block

def make_assignments(data, table_format="XMA", labels=["X"], units=["PPM"], ):

    data = np.atleast_2d(data)

    block = {}

    if not len(data):
        return block

    #if not len(data[0]) >= 3:
    #    return block

    block["DATA CLASS"] = "PEAK ASSIGNMENTS"
    block["NPOINTS"] = str(len(data))

    for label, unit in zip(labels, units):
        block[label + "UNITS"] = unit

    block["PEAK ASSIGNMENTS"] = "(%s)"%table_format

    multcenterfound = False

    #print(data)
    for row in data:
        row = list(map(str,row))
        #default for nmrpred is atom, shift, mult, x, y
        #rearrange to shift, mult, atom
        try:
            if len(table_format) == 4: #XYMA what was this for?
                row = [row[1], "", row[2], row[0]]
            else:
                row = [row[1], row[2], row[0]]
            multcenterfound = True
        except:
            continue
        try:
            row[table_format.index("A")] = "<%s>"%int(float(row[table_format.index("A")]))
        except:
            row[table_format.index("A")] = "<%s>"%("NA")
        row[table_format.index("M")] = "<%s>"%row[table_format.index("M")]
        block["PEAK ASSIGNMENTS"] += "\n(%s)"%(", ".join(row))

    if multcenterfound == False:
        return {}

    return block


def make_peaktable(data, table_format="XY..XY", labels=["X","Y"], units=["PPM","ARBITRARY UNITS"], yscale=None):

    data = np.atleast_2d(data)

    block = {}

    if not len(data):
        return block

    if not len(data[0]) >= 3:
        return block

    block["DATA CLASS"] = "PEAK TABLE"
    block["NPOINTS"] = str(len(data))

    for label, unit in zip(labels, units):
        block[label + "UNITS"] = unit

    block["PEAK TABLE"] = "(%s)"%table_format

    peakposfound = False

    #skip this: output peak intensties as unscaled
    #if yscale:
    #    dictofpeaks = {}
    #    for row in data:
    #        try:
    #            idx = round(float(row[3]), 2)
    #            peakposfound = True
    #        except:
    #            continue
    #        if idx not in dictofpeaks: dictofpeaks[idx] = float(row[4])
    #        else: dictofpeaks[idx] += float(row[4])
    #    if dictofpeaks:
    #        peakmax = max(dictofpeaks.values())
    #    else:
    #        peakmax = 1.0
    #    scalefactor = yscale/peakmax
    #    #scalefactor = 1.0
    #else:
    #    scalefactor = 1.0

    peakposfound = True
    scalefactor = 1.0

    if peakposfound == False:
        return {}

    for row in data:
        #row = list(map(str,row))
        #default for nmrpred peaklist is atom, shift, mult, x, y
        try:
            row = [str(row[3]), str(float(row[4])*scalefactor)]
        except:
            continue
        block["PEAK TABLE"] += "\n(%s)"%(", ".join(row))

    return block


def make_couptable(data):
    block = {}

    #C,2,57.97,s,
    #O,3,,,
    #H,4,1.2,t,6.7

    table = []
    for line in data:
        #print(line)
        coup = line[4]
        try:
            atom = str(int(line[1]))
        except:
            atom = str(line[1])
        if coup:
            coup = coup.split(',')
            for j in coup:
                table.append([j,atom])

    if table:
        block['.COUPLING CONSTANTS'] = "J(A)"

    if table:
        for line in table:
            if (line[0] == "NA") or (float(line[0]) == "0"):
                continue
            block['.COUPLING CONSTANTS'] += "\n%s(%s)"%(line[0],line[1])

    return block


def make_fid(data, data_type="NMR FID",    labels=["X","R","I","N"],
                                            names=["TIME","FID/REAL","FID/IMAG", "PAGE NUMBER"],
                                            units=["SECONDS","ARBITRARY UNITS","ARBITRARY UNITS",""],
                                            types=["INDEPENDENT", "DEPENDENT","DEPENDENT","PAGE"],
             compression="DIF",):

    #should work for 1d spec with imag data too...

    block = {}
    pages = []
    footer = {}

    block.update({"DATA CLASS":"NTUPLES"})

    block.update({  "NTUPLES":data_type,
                    "VAR_NAME":names,
                    "SYMBOL":labels,
                    "VAR_TYPE":types,
                    "VAR_FORM":["AFFN","ADSF","ADSF","AFFN"],
                    "VAR_DIM":[],
                    "UNITS":[],
                    "FIRST":[],
                    "LAST":[],
                    "MIN":[],
                    "MAX":[],
                    "FACTOR":[],})



    #data = data.T

    xdata, xscale = scale_data(data[:,0],'xauto')
    ydata, yscale = scale_data(data[:,1:].ravel(),'yauto')
    rdata, idata = ydata.reshape((xdata.size,2)).T

    newblock = get_range(xdata, xscale, dimlabel="", units=units[0])
    for k in newblock:
        if k in block:          block[k].append(newblock[k])
        elif k == "NPOINTS":    block["VAR_DIM"].append(newblock[k])
    newblock = get_range(rdata, yscale, dimlabel="", units=units[1])
    for k in newblock:
        if k in block:          block[k].append(newblock[k])
        elif k == "NPOINTS":    block["VAR_DIM"].append(newblock[k])
    newblock = get_range(idata, yscale, dimlabel="", units=units[2])
    for k in newblock:
        if k in block:          block[k].append(newblock[k])
        elif k == "NPOINTS":    block["VAR_DIM"].append(newblock[k])

    pagedic = {"VAR_DIM":2,"UNITS":"","FIRST":1,"LAST":2,"MIN":1,"MAX":2,"FACTOR":1}
    for k in pagedic:
        if k in block:          block[k].append(pagedic[k])
        elif k == "NPOINTS":    block["VAR_DIM"].append(pagedic[k])


    for k in block:
        if type(block[k]) is list:
            block[k] = ",".join(map(str,block[k]))

    newblock, _ = xy_to_dx( xdata, rdata,
                            xprec=0, yprec=0,
                            cols=80,
                            form=compression,
                            xsym=labels[0], ysym=labels[1])

    page = make_page()
    page["PAGE"]="N=1"
    page["DATA TABLE"] = newblock["XYDATA"]
    pages.append(page)

    newblock, _ = xy_to_dx( xdata, idata,
                            xprec=0, yprec=0,
                            cols=80,
                            form=compression,
                            xsym=labels[0], ysym=labels[2])

    page = make_page()
    page["PAGE"]="N=2"
    page["DATA TABLE"] = newblock["XYDATA"]
    pages.append(page)

    footer.update({"END NTUPLES":data_type})

    return block, pages, footer



def make_2d_fid_varian(f, compression="DIF"):
    return


def make_page():

    block = {"PAGE":None,
            "NPOINTS":None,
            "FIRST":None,
            "DATA TABLE":None,}

    return block

def make_structureblock(molfile):
    b = block("CS")
    b.add_mol(molfile)
    return b

def make_spectrumblock(specfile, filetype='csv', compression="DIF"):
    b = block("DX","NMR SPECTRUM")
    b.add_1d_spectrum(specfile, filetype, compression)
    return b

def make_assignmentblock(assignfile, filetype='csv'):
    b = block("DX","NMR PEAK ASSIGNMENTS")
    b.add_assignments(assignfile, filetype)
    return b

def make_1dfidblock(fidfile, filetype="csv", compression="DIF",neg_imag=False):
    b = block("DX","NMR FID")
    b.add_1d_fid(fidfile, filetype, compression, neg_imag=False)
    return b



def remove_digital_filter(dic, data, truncate=True, post_proc=False):
    #from nmrglue

    if 'acqus' not in dic:
        raise ValueError("dictionary does not contain acqus parameters")

    if 'DECIM' not in dic['acqus']:
        raise ValueError("dictionary does not contain DECIM parameter")
    decim = dic['acqus']['DECIM']

    if 'DSPFVS' not in dic['acqus']:
        raise ValueError("dictionary does not contain DSPFVS parameter")
    dspfvs = dic['acqus']['DSPFVS']

    if 'GRPDLY' not in dic['acqus']:
        grpdly = 0
    else:
        grpdly = dic['acqus']['GRPDLY']

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
        else:   # loop up the phase in the table
            if dspfvs not in bruker_dsp_table:
                raise ValueError("dspfvs not in lookup table")
            if decim not in bruker_dsp_table[dspfvs]:
                raise ValueError("decim not in lookup table")
            phase = ng.bruker.bruker_dsp_table[dspfvs][decim]

    if truncate_grpdly:     # truncate the phase
        phase = np.floor(phase)

    return phase


def make_tupleblock(data_type, ncol=2):

    block = {"DATA CLASS":"NTUPLES",
             "NTUPLES":data_type,
             "VAR_NAME":[""]*ncol,
             "SYMBOL":[""]*ncol,
             ".NUCLEUS":[""]*ncol,
             "VAR_TYPE":[""]*ncol,
             "VAR_FORM":[""]*ncol,
             "VAR_DIM":[""]*ncol,
             "UNITS":[""]*ncol,
             "FIRST":[""]*ncol,
             "LAST":[""]*ncol,
             "MIN":[""]*ncol,
             "MAX":[""]*ncol,
             "FACTOR":[""]*ncol,
            }

    return block


def read_bruker_1d_fid(fpath, compression="DIF"):

    import nmrglue as ng

    block = {}

    dic, data = ng.bruker.read(fpath)
    udic = ng.bruker.guess_udic(dic, data)

    #data as x,y in columns
    uc_x = ng.fileiobase.uc_from_udic(udic,0)
    x_ppm = uc_x.sec_scale()

    try:
        grpdly = remove_digital_filter(dic, data)
    except:
        grpdly = 0
    delay = uc_x.us(grpdly)
    block.update({"$GRPDLY":str(grpdly)})

    x_quad = dic['acqus']['AQ_mod']
    if x_quad == 0:
        x_quad = "SINGLE" #real only?
    if x_quad == 1:
        x_quad = "SEQUENTIAL" #alternating real, complex
    if x_quad >= 2:
        x_quad = "SIMULTANEOUS" #simulateneous detection of real, complex

    block.update({"SPECTROMETER/DATA SYSTEM":"BRUKER",
         "TEMPERATURE":str(float(dic['acqus']["TE"]) - 273.15),
         ".OBSERVE FREQUENCY":udic[0]['obs'],
         ".OBSERVE NUCLEUS":udic[0]['label'],
         ".SOLVENT NAME":dic['acqus']["SOLVENT"],
         ".DELAY":(0, 0 + uc_x.us(1)/2 if "SEQ" in x_quad else 0),
         ".ACQUISITION MODE":x_quad,
         ".PULSE SEQUENCE":dic['acqus']["PULPROG"],
        })

    return block, np.column_stack((x_ppm, data.real, data.imag))


def make_varian_1d_fid(fpath, compression="DIF"):

    import nmrglue as ng

    block = {}

    #try reading data
    dic, data = ng.varian.read(fpath)

    udic = ng.varian.guess_udic(dic, data)
    extract_varian.varian_to_udic(dic, udic)

    #data as x,y in columns
    uc_x = ng.fileiobase.uc_from_udic(udic,0)
    x_ppm = uc_x.sec_scale()


    x_quad = dic['procpar']['proc']['values'][0]
    if x_quad in ('ft', 'lp'):
        x_quad = "SIMULTANEOUS" #simulateneous detection of real, complex
    elif x_quad == 'rft':
        x_quad = "SEQUENTIAL" #alternating real, complex
    else:
        x_quad = "UNKNOWN"

    block.update({"SPECTROMETER/DATA SYSTEM":"VARIAN/AGILENT",
         "TEMPERATURE":str(float(dic['procpar']["temp"]['values'][0])),
         ".OBSERVE FREQUENCY":udic[0]['obs'],
         ".OBSERVE NUCLEUS":udic[0]['label'],
         ".DELAY":(0, 0),
         ".SOLVENT NAME":udic["solvent"],
         ".ACQUISITION MODE":x_quad,
         ".PULSE SEQUENCE":udic["pulseseq"],
        })


    return block, np.column_stack((x_ppm, data.real, data.imag))


def make_bruker_1d_spec(fpath, compression="DIF"):

    import nmrglue as ng

    block = {}

    dic, data = ng.bruker.read_pdata(fpath)
    udic = ng.bruker.guess_udic(dic, data)

    #print(dic)
    #print(udic)
    #raise

    #data as x,y in columns
    uc_x = ng.fileiobase.uc_from_udic(udic,0)
    x_ppm = uc_x.ppm_scale()

    block.update({"SPECTROMETER/DATA SYSTEM":"BRUKER",
         "TEMPERATURE":str(float(dic['acqus']["TE"]) - 273.15),
         ".OBSERVE FREQUENCY":udic[0]['obs'],
         ".OBSERVE NUCLEUS":udic[0]['label'],
         ".SOLVENT NAME":dic['acqus']["SOLVENT"],
         ".PULSE SEQUENCE":dic['acqus']["PULPROG"],
        })

    return block, np.column_stack((x_ppm, data.real))


def make_varian_1d_spec(fpath, compression="DIF"):

    import nmrglue as ng

    block = {}

    udic, dic, data = extract_varian.get_processed_data(fpath)

    #print(dic)
    #print(udic)
    #raise

    #data as x,y in columns
    uc_x = ng.fileiobase.uc_from_udic(udic,0)
    x_ppm = uc_x.ppm_scale()

    block.update({"SPECTROMETER/DATA SYSTEM":"VARIAN/AGILENT",
         "TEMPERATURE":str(float(dic['procpar']["temp"]['values'][0])),
         ".OBSERVE FREQUENCY":udic[0]['obs'],
         ".OBSERVE NUCLEUS":udic[0]['label'],
         ".SOLVENT NAME":udic["solvent"],
         ".PULSE SEQUENCE":udic["pulseseq"],
        })

    return block, np.column_stack((x_ppm, data.real))


def make_bruker_2d_fid(fpath, compression="DIF"):

    import nmrglue as ng

    block = {}
    pages = []
    footer = {}

    dic, data = ng.bruker.read(fpath)
    udic = ng.bruker.guess_udic(dic, data)
    fix_udic_bruker(udic, dic)
    uc_x = ng.fileiobase.uc_from_udic(udic,1) #direct
    uc_y = ng.fileiobase.uc_from_udic(udic,0) #indirect

    try:
        grpdly = remove_digital_filter(dic, data)
    except:
        grpdly = 0
    delay = uc_x.us(grpdly)
    block.update({"$GRPDLY":str(grpdly)})

    x_quad = dic['acqus']['AQ_mod']
    if x_quad == 0:
        x_quad = "SINGLE" #real only?
    if x_quad == 1:
        x_quad = "SEQUENTIAL" #alternating real, complex
    if x_quad >= 2:
        x_quad = "SIMULTANEOUS" #simulateneous detection of real, complex

    y_quad = udic[0]['encoding'].upper()
    if "MAG" in y_quad: y_quad = "NOT PHASE SENSITIVE"

    block.update({"SPECTROMETER/DATA SYSTEM":"BRUKER",
         "TEMPERATURE":str(float(dic['acqus']["TE"]) - 273.15),
         ".OBSERVE FREQUENCY":udic[1]['obs'],
         ".OBSERVE NUCLEUS":udic[1]['label'],
         ".SOLVENT NAME":dic['acqus']["SOLVENT"],
         #".DELAY":[delay,delay + uc_x.us(1)/2 if "SEQ" in x_quad else delay],
         ".DELAY":(0, 0 + uc_x.us(1)/2 if "SEQ" in x_quad else 0),
         ".ACQUISITION MODE":x_quad,
         ".ACQUISITION SCHEME":y_quad,
         ".PULSE SEQUENCE":dic['acqus']["PULPROG"],
        })

        #not phase sens: for magn data or processed spectrum, 1R, 2R, 3R...

        #tppi: shift spectrum, T1: 1R, 2I, 3R, 4I,...

        #states: cos and sin modulated fids, T1: 1R, 1I, 2R, 2I, ...
        #states tppi: T1: 1R, 1I, 2R, 2I, ...
        #echo antiecho: p and n type fids, T1: 1R, 1I, 2R, 2I,... shuffle 1R=(1R+1I), 1I=(1R-1I)..


    x_unscaled = uc_x.sec_scale()
    xdata, xscale = scale_data(x_unscaled, scale='xauto')
    y_unscaled = uc_y.sec_scale()
    ydata, yscale = scale_data(y_unscaled, scale='xauto')
    z_unscaled = data
    zdata, zscale = scale_data(z_unscaled, scale='yauto')


    if "STATES" or "ECHO" in y_quad:
        ydata = np.repeat(ydata, 2)[:ydata.size]

    iscomplex = np.iscomplexobj(zdata)

    ntuples = make_tupleblock("nD NMR FID", 4 if iscomplex else 3)

    ntuples["VAR_NAME"] = ["TIME1","TIME2","FID/REAL","FID/IMAG"]
    ntuples["SYMBOL"] = ["T1","T2","R","I"]
    ntuples[".NUCLEUS"] = [udic[0]['label'],udic[1]['label'],"",""]
    ntuples["VAR_TYPE"] = ["INDEPENDENT","INDEPENDENT","DEPENDENT","DEPENDENT"]
    ntuples["VAR_FORM"] = ["AFFN","AFFN","ADSF","ADSF"]
    ntuples["VAR_DIM"] = [zdata.shape[0], zdata.shape[1], zdata.shape[1], zdata.shape[1],]
    ntuples["UNITS"] = ["SECONDS", "SECONDS", "ARBITRARY UNITS", "ARBITRARY UNITS"]
    ntuples["FIRST"] = [ydata[0]*yscale, xdata[0]*xscale, zdata[0,0].real*zscale, zdata[0,0].imag*zscale]
    ntuples["LAST"] = [ydata[-1]*yscale, xdata[-1]*xscale, zdata[-1,-1].real*zscale, zdata[-1,-1].imag*zscale]
    ntuples["MIN"] = [np.min(ydata)*yscale, np.min(xdata)*xscale, np.min(zdata.real)*zscale, np.min(zdata.imag)*zscale]
    ntuples["MAX"] = [np.max(ydata)*yscale, np.max(xdata)*xscale, np.max(zdata.real)*zscale, np.max(zdata.imag)*zscale]
    ntuples["FACTOR"] = [yscale, xscale, zscale, zscale]

    block.update(ntuples)



    if not iscomplex:
        for k in block:
            if type(block[k]) is list:
                block[k] = block[k][:-1]


    for i in range(len(ydata)):

        #print('$$printing page %s/%s'%(i+1,len(ydata)), file=sys.stderr)

        page = make_page()
        page["PAGE"] = " T1=%s"%(ydata[i]*yscale)
        page["FIRST"] = ntuples["FIRST"][:]
        page["FIRST"][0] = ydata[i]*yscale
        page["FIRST"] = ",".join(map(str,page["FIRST"]))

        newblock, _ = xy_to_dx( xdata, zdata[i].real,
                                xprec=0, yprec=0,
                                cols=80,
                                form=compression,
                                xsym=ntuples["SYMBOL"][1], ysym=ntuples["SYMBOL"][2])

        page["DATA TABLE"] = newblock["XYDATA"]

        pages.append(page)

        if iscomplex:

            page = make_page()
            page["PAGE"] = " T1=%s"%(ydata[i]*yscale)
            page["FIRST"] = ntuples["FIRST"][:]
            page["FIRST"][0] = ydata[i]*yscale
            page["FIRST"] = ",".join(map(str,page["FIRST"]))

            newblock, _ = xy_to_dx( xdata, zdata[i].imag,
                                    xprec=0, yprec=0,
                                    cols=80,
                                    form=compression,
                                    xsym=ntuples["SYMBOL"][1], ysym=ntuples["SYMBOL"][3])

            page["DATA TABLE"] = newblock["XYDATA"]

            pages.append(page)


    footer.update({"END NTUPLES":"nD NMR FID"})

    for k in block:
        if type(block[k]) is list:
            block[k] = ",".join(map(str,block[k]))

    #plt.plot(data[0,:])
    #plt.show()


    return block, pages, footer


def fix_udic_bruker(udic, dic):

    #work around for older version of nmrglue?

    import nmrglue as ng

    for bruk_file in dic:

        if "acqu" in bruk_file:
            acqu_file = bruk_file
        else:
            continue

        if "SW_p" in dic[acqu_file] and "SW_h" not in dic[acqu_file]:
            dic[acqu_file]["SW_h"] = dic[acqu_file]["SW_p"]
        elif "SFO1" in dic[acqu_file] and "SW" in dic[acqu_file]:
            dic[acqu_file]["SW_h"] = dic[acqu_file]["SFO1"] * dic[acqu_file]["SW"]
        else:
            continue

    for dim in udic:

        if dim == "ndim": continue

        curr_dim = udic[dim]
        if curr_dim['label'] == "X":

            try:
                ng.bruker.add_axis_to_udic(udic, dic, dim, False)
            except:
                pass


def make_bruker_2d_spec(fpath, compression="DIF"):

    import nmrglue as ng

    block = {}
    pages = []
    footer = {}

    #print("DEUBG")
    dic, data = ng.bruker.read_pdata( fpath )
    #print(dic)
    udic = ng.bruker.guess_udic(dic, data)
    fix_udic_bruker(udic, dic)
    #print(udic)
    uc_x = ng.fileiobase.uc_from_udic(udic,1) #direct
    uc_y = ng.fileiobase.uc_from_udic(udic,0) #indirect


    block.update({"SPECTROMETER/DATA SYSTEM":"BRUKER",
         "TEMPERATURE":str(float(dic['acqus']["TE"]) - 273.15),
         ".OBSERVE FREQUENCY":udic[1]['obs'],
         ".OBSERVE NUCLEUS":udic[1]['label'],
         ".SOLVENT NAME":dic['acqus']["SOLVENT"],
         ".PULSE SEQUENCE":dic['acqus']["PULPROG"],
        })

    x_unscaled = uc_x.ppm_scale()
    xdata, xscale = scale_data(x_unscaled, scale='xauto')
    y_unscaled = uc_y.ppm_scale() #actual values may be repeated depeding on scheme (sim vs seq)???
    ydata, yscale = scale_data(y_unscaled, scale='xauto')
    z_unscaled = data
    zdata, zscale = scale_data(z_unscaled, scale='yauto')

    #print(x_unscaled)
    #print(xdata, xscale)
    #print(y_unscaled)
    #print(ydata, yscale )
    #raise ValueError()

    xdata = xdata.astype(int)
    ydata = ydata.astype(int)
    zdata = zdata.astype(int)

    ntuples = make_tupleblock("nD NMR SPECTRUM", 3)

    ntuples["VAR_NAME"] = ["FREQUENCY1","FREQUENCY2","SPECTRUM"]
    ntuples["SYMBOL"] = ["F1","F2","Y"]
    ntuples[".NUCLEUS"] = [udic[0]['label'],udic[1]['label'],""] #indirect and observe nuc
    ntuples["VAR_TYPE"] = ["INDEPENDENT","INDEPENDENT","DEPENDENT"]
    ntuples["VAR_FORM"] = ["AFFN","AFFN","ADSF"]
    ntuples["VAR_DIM"] = [zdata.shape[0], zdata.shape[1], zdata.shape[1]]
    ntuples["UNITS"] = ["PPM", "PPM", "ARBITRARY UNITS"]
    ntuples["FIRST"] = [ydata[0]*yscale, xdata[0]*xscale, zdata[0,0].real*zscale,]
    ntuples["LAST"] = [ydata[-1]*yscale, xdata[-1]*xscale, zdata[-1,-1].real*zscale]
    ntuples["MIN"] = [np.min(ydata)*yscale, np.min(xdata)*xscale, np.min(zdata.real)*zscale,]
    ntuples["MAX"] = [np.max(ydata)*yscale, np.max(xdata)*xscale, np.max(zdata.real)*zscale,]
    ntuples["FACTOR"] = [yscale, xscale, zscale,]

    block.update(ntuples)


    for i in range(len(ydata)):

        #print('$$printing page %s/%s'%(i+1,len(ydata)), file=sys.stderr)

        page = make_page()
        page["PAGE"] = " T1=%s"%(ydata[i]*yscale)
        page["FIRST"] = ntuples["FIRST"][:]
        page["FIRST"][0] = ydata[i]*yscale
        page["FIRST"] = ",".join(map(str,page["FIRST"]))

        newblock, _ = xy_to_dx( xdata, zdata[i].real,
                                xprec=0, yprec=0,
                                cols=80,
                                form=compression,
                                xsym=ntuples["SYMBOL"][1], ysym=ntuples["SYMBOL"][2])

        page["DATA TABLE"] = newblock["XYDATA"]

        pages.append(page)


    footer.update({"END NTUPLES":"nD NMR SPECTRUM"})

    for k in block:
        if type(block[k]) is list:
            block[k] = ",".join(map(str,block[k]))

    return block, pages, footer


def make_varian_2d_spec(fpath, compression="DIF"):

    import nmrglue as ng

    block = {}
    pages = []
    footer = {}

    #print("DEUBG")
    udic, dic, data = extract_varian.get_processed_data(fpath)

    #print(udic)
    uc_x = ng.fileiobase.uc_from_udic(udic,1) #direct
    uc_y = ng.fileiobase.uc_from_udic(udic,0) #indirect


    block.update({"SPECTROMETER/DATA SYSTEM":"VARIAN/AGILENT",
         "TEMPERATURE":str(float(dic['procpar']["temp"]['values'][0])),
         ".OBSERVE FREQUENCY":udic[1]['obs'],
         ".OBSERVE NUCLEUS":udic[1]['label'],
         ".SOLVENT NAME":udic["solvent"],
         ".PULSE SEQUENCE":udic["pulseseq"],
        })


    uc_x = ng.fileiobase.uc_from_udic(udic, 1)
    x_units = udic[1]['units']
    func = "%s_scale"%(x_units.lower())
    x_unscaled = getattr(uc_x, func)()
    xdata, xscale = scale_data(x_unscaled, scale='xauto')

    uc_y = ng.fileiobase.uc_from_udic(udic, 0)
    y_units = udic[0]['units']
    func = "%s_scale"%(y_units.lower())
    y_unscaled = getattr(uc_y, func)()
    ydata, yscale = scale_data(y_unscaled, scale='yauto')

    z_unscaled = data
    zdata, zscale = scale_data(z_unscaled, scale='yauto')


    xdata = xdata.astype(int)
    ydata = ydata.astype(int)
    zdata = zdata.astype(int)

    ntuples = make_tupleblock("nD NMR SPECTRUM", 3)

    ntuples["VAR_NAME"] = ["FREQUENCY1","FREQUENCY2","SPECTRUM"]
    ntuples["SYMBOL"] = ["F1","F2","Y"]
    ntuples[".NUCLEUS"] = [udic[0]['label'],udic[1]['label'],""] #indirect and observe nuc
    ntuples["VAR_TYPE"] = ["INDEPENDENT","INDEPENDENT","DEPENDENT"]
    ntuples["VAR_FORM"] = ["AFFN","AFFN","ADSF"]
    ntuples["VAR_DIM"] = [zdata.shape[0], zdata.shape[1], zdata.shape[1]]
    ntuples["UNITS"] = ["PPM", "PPM", "ARBITRARY UNITS"]
    ntuples["FIRST"] = [ydata[0]*yscale, xdata[0]*xscale, zdata[0,0].real*zscale,]
    ntuples["LAST"] = [ydata[-1]*yscale, xdata[-1]*xscale, zdata[-1,-1].real*zscale]
    ntuples["MIN"] = [np.min(ydata)*yscale, np.min(xdata)*xscale, np.min(zdata.real)*zscale,]
    ntuples["MAX"] = [np.max(ydata)*yscale, np.max(xdata)*xscale, np.max(zdata.real)*zscale,]
    ntuples["FACTOR"] = [yscale, xscale, zscale,]

    if x_units.lower() == "hz":
        ntuples["UNITS"][0] = "HZ"

    block.update(ntuples)


    for i in range(len(ydata)):

        #print('$$printing page %s/%s'%(i+1,len(ydata)), file=sys.stderr)

        page = make_page()
        page["PAGE"] = " T1=%s"%(ydata[i]*yscale)
        page["FIRST"] = ntuples["FIRST"][:]
        page["FIRST"][0] = ydata[i]*yscale
        page["FIRST"] = ",".join(map(str,page["FIRST"]))

        newblock, _ = xy_to_dx( xdata, zdata[i].real,
                                xprec=0, yprec=0,
                                cols=80,
                                form=compression,
                                xsym=ntuples["SYMBOL"][1], ysym=ntuples["SYMBOL"][2])

        page["DATA TABLE"] = newblock["XYDATA"]

        pages.append(page)


    footer.update({"END NTUPLES":"nD NMR SPECTRUM"})

    for k in block:
        if type(block[k]) is list:
            block[k] = ",".join(map(str,block[k]))

    return block, pages, footer


def make_varian_2d_fid(fpath, compression="DIF"):

    import nmrglue as ng

    block = {}
    pages = []
    footer = {}

    #try reading data
    dic, data = ng.varian.read(fpath)

    #for biopack, may get confused (psudo 3d?), reload as 2d
    ndim = extract_varian.get_dim(dic)
    if ndim == 2:
        dic, data = ng.varian.read(fpath, as_2d=True)

    #update udic using procpar
    udic = ng.varian.guess_udic(dic, data)
    extract_varian.varian_to_udic(dic, udic)


    uc_x = ng.fileiobase.uc_from_udic(udic,1) #direct
    uc_y = ng.fileiobase.uc_from_udic(udic,0) #indirect

    #

    x_quad = dic['procpar']['proc']['values'][0]
    if x_quad in ('ft', 'lp'):
        x_quad = "SIMULTANEOUS" #simulateneous detection of real, complex
    elif x_quad == 'rft':
        x_quad = "SEQUENTIAL" #alternating real, complex
    else:
        x_quad = "UNKNOWN"

    coef = extract_varian.get_2d_coef(udic, dic['procpar'])
    coef = list(map(int, coef.strip().split()))
    if not coef or len(coef) <= 4:
        y_quad = "NOT PHASE SENSITIVE"
    else:
        y_quad = "UNKNOWN"
        if np.count_nonzero(coef) == 1:
            y_quad = "NOT PHASE SENSITIVE"
        if np.count_nonzero(coef) == 2:
            y_quad = "STATES"
        if np.count_nonzero(coef) == 4:
            y_quad = "ECHO-ANTIECHO"
        phase_par = dic['procpar']['phase']['values'][0]
        if phase_par.endswith('3'):
            y_quad = "TPPI"
        if phase_par.endswith('4'):
            y_quad = "STATES-TPPI"


    block.update({"SPECTROMETER/DATA SYSTEM":"VARIAN",
         "TEMPERATURE":str(float(dic['procpar']["temp"]['values'][0])),
         ".OBSERVE FREQUENCY":udic[1]['obs'],
         ".OBSERVE NUCLEUS":udic[1]['label'],
         ".SOLVENT NAME":udic["solvent"],
         ".DELAY":(0, 0),
         ".ACQUISITION MODE":x_quad,
         ".ACQUISITION SCHEME":y_quad,
         ".PULSE SEQUENCE":udic["pulseseq"],
        })

        #not phase sens: for magn data or processed spectrum, 1R, 2R, 3R...

        #tppi: shift spectrum, T1: 1R, 2I, 3R, 4I,...

        #states: cos and sin modulated fids, T1: 1R, 1I, 2R, 2I, ...
        #states tppi: T1: 1R, 1I, 2R, 2I, ...
        #echo antiecho: p and n type fids, T1: 1R, 1I, 2R, 2I,... shuffle 1R=(1R+1I), 1I=(1R-1I)..


    x_unscaled = uc_x.sec_scale()
    xdata, xscale = scale_data(x_unscaled, scale='xauto')
    y_unscaled = uc_y.sec_scale()
    ydata, yscale = scale_data(y_unscaled, scale='xauto')
    z_unscaled = data
    zdata, zscale = scale_data(z_unscaled, scale='yauto')


    if "STATES" or "ECHO" in y_quad:
        ydata = np.repeat(ydata, 2)[:ydata.size]

    iscomplex = np.iscomplexobj(zdata)

    ntuples = make_tupleblock("nD NMR FID", 4 if iscomplex else 3)

    ntuples["VAR_NAME"] = ["TIME1","TIME2","FID/REAL","FID/IMAG"]
    ntuples["SYMBOL"] = ["T1","T2","R","I"]
    ntuples[".NUCLEUS"] = [udic[0]['label'],udic[1]['label'],"",""]
    ntuples["VAR_TYPE"] = ["INDEPENDENT","INDEPENDENT","DEPENDENT","DEPENDENT"]
    ntuples["VAR_FORM"] = ["AFFN","AFFN","ADSF","ADSF"]
    ntuples["VAR_DIM"] = [zdata.shape[0], zdata.shape[1], zdata.shape[1], zdata.shape[1],]
    ntuples["UNITS"] = ["SECONDS", "SECONDS", "ARBITRARY UNITS", "ARBITRARY UNITS"]
    ntuples["FIRST"] = [ydata[0]*yscale, xdata[0]*xscale, zdata[0,0].real*zscale, zdata[0,0].imag*zscale]
    ntuples["LAST"] = [ydata[-1]*yscale, xdata[-1]*xscale, zdata[-1,-1].real*zscale, zdata[-1,-1].imag*zscale]
    ntuples["MIN"] = [np.min(ydata)*yscale, np.min(xdata)*xscale, np.min(zdata.real)*zscale, np.min(zdata.imag)*zscale]
    ntuples["MAX"] = [np.max(ydata)*yscale, np.max(xdata)*xscale, np.max(zdata.real)*zscale, np.max(zdata.imag)*zscale]
    ntuples["FACTOR"] = [yscale, xscale, zscale, zscale]

    block.update(ntuples)



    if not iscomplex:
        for k in block:
            if type(block[k]) is list:
                block[k] = block[k][:-1]


    for i in range(len(ydata)):

        #print('$$printing page %s/%s'%(i+1,len(ydata)), file=sys.stderr)

        page = make_page()
        page["PAGE"] = " T1=%s"%(ydata[i]*yscale)
        page["FIRST"] = ntuples["FIRST"][:]
        page["FIRST"][0] = ydata[i]*yscale
        page["FIRST"] = ",".join(map(str,page["FIRST"]))

        newblock, _ = xy_to_dx( xdata, zdata[i].real,
                                xprec=0, yprec=0,
                                cols=80,

                                form=compression,
                                xsym=ntuples["SYMBOL"][1], ysym=ntuples["SYMBOL"][2])

        page["DATA TABLE"] = newblock["XYDATA"]

        pages.append(page)

        if iscomplex:

            page = make_page()
            page["PAGE"] = " T1=%s"%(ydata[i]*yscale)
            page["FIRST"] = ntuples["FIRST"][:]
            page["FIRST"][0] = ydata[i]*yscale
            page["FIRST"] = ",".join(map(str,page["FIRST"]))

            newblock, _ = xy_to_dx( xdata, zdata[i].imag,
                                    xprec=0, yprec=0,
                                    cols=80,
                                    form=compression,
                                    xsym=ntuples["SYMBOL"][1], ysym=ntuples["SYMBOL"][3])

            page["DATA TABLE"] = newblock["XYDATA"]

            pages.append(page)


    footer.update({"END NTUPLES":"nD NMR FID"})

    for k in block:
        if type(block[k]) is list:
            block[k] = ",".join(map(str,block[k]))

    #plt.plot(data[0,:])
    #plt.show()


    return block, pages, footer

def make_nmrml_2d_spec(meta, udic, data, compression="DIF"):

    import nmrglue as ng

    block = {}
    pages = []
    footer = {}

    uc_x = ng.fileiobase.uc_from_udic(udic,1) #direct
    uc_y = ng.fileiobase.uc_from_udic(udic,0) #indirect

    #print(meta)
    #print(udic)


    block.update({"SPECTROMETER/DATA SYSTEM":"N/A",
         "TEMPERATURE":str(float(udic[1]['temp'])) if udic[1]["temp"] else None,
         ".OBSERVE FREQUENCY":udic[1]['obs'],
         ".OBSERVE NUCLEUS":udic[1]['label'],
         ".SOLVENT NAME":meta['solvent'],
         ".PULSE SEQUENCE":"2D HSQC",
        })

    x_unscaled = uc_x.ppm_scale()
    xdata, xscale = scale_data(x_unscaled, scale='xauto')
    y_unscaled = uc_y.ppm_scale()
    ydata, yscale = scale_data(y_unscaled, scale='xauto')
    z_unscaled = data
    zdata, zscale = scale_data(z_unscaled, scale='yauto')

    #print(x_unscaled)
    #print(xdata, xscale)
    #print(y_unscaled)
    #print(ydata, yscale )
    #raise ValueError()
    #print(zdata.shape)

    xdata = xdata.astype(int)
    ydata = ydata.astype(int)
    zdata = zdata.astype(int)

    ntuples = make_tupleblock("nD NMR SPECTRUM", 3)

    ntuples["VAR_NAME"] = ["FREQUENCY1","FREQUENCY2","SPECTRUM"]
    ntuples["SYMBOL"] = ["F1","F2","Y"]
    ntuples[".NUCLEUS"] = [udic[0]['label'],udic[1]['label'],""] #indirect and observe nuc
    ntuples["VAR_TYPE"] = ["INDEPENDENT","INDEPENDENT","DEPENDENT"]
    ntuples["VAR_FORM"] = ["AFFN","AFFN","ADSF"]
    ntuples["VAR_DIM"] = [zdata.shape[0], zdata.shape[1], zdata.shape[1]]
    ntuples["UNITS"] = ["PPM", "PPM", "ARBITRARY UNITS"]
    ntuples["FIRST"] = [ydata[0]*yscale, xdata[0]*xscale, zdata[0,0].real*zscale,]
    ntuples["LAST"] = [ydata[-1]*yscale, xdata[-1]*xscale, zdata[-1,-1].real*zscale]
    ntuples["MIN"] = [np.min(ydata)*yscale, np.min(xdata)*xscale, np.min(zdata.real)*zscale,]
    ntuples["MAX"] = [np.max(ydata)*yscale, np.max(xdata)*xscale, np.max(zdata.real)*zscale,]
    ntuples["FACTOR"] = [yscale, xscale, zscale,]

    block.update(ntuples)


    for i in range(len(ydata)):

        #print('$$printing page %s/%s'%(i+1,len(ydata)), file=sys.stderr)

        page = make_page()
        page["PAGE"] = " T1=%s"%(ydata[i]*yscale)
        page["FIRST"] = ntuples["FIRST"][:]
        page["FIRST"][0] = ydata[i]*yscale
        page["FIRST"] = ",".join(map(str,page["FIRST"]))

        newblock, _ = xy_to_dx( xdata, zdata[i].real,
                                xprec=0, yprec=0,
                                cols=80,
                                form=compression,
                                xsym=ntuples["SYMBOL"][1], ysym=ntuples["SYMBOL"][2])

        page["DATA TABLE"] = newblock["XYDATA"]

        pages.append(page)


    footer.update({"END NTUPLES":"nD NMR SPECTRUM"})

    for k in block:
        if type(block[k]) is list:
            block[k] = ",".join(map(str,block[k]))

    return block, pages, footer


def make_2d_spec_json(filename, compression="DIF"):



    block = {}
    pages = []
    footer = {}

    y, x, z = read_json_2d(filename)

    xdata, xscale = scale_data(x, scale='xauto')
    ydata, yscale = scale_data(y, scale='xauto')
    zdata, zscale = scale_data(z, scale='yauto')

    xdata = xdata.astype(int)
    ydata = ydata.astype(int)
    zdata = zdata.astype(int)


    ntuples = make_tupleblock("nD NMR SPECTRUM", 3)

    ntuples["VAR_NAME"] = ["FREQUENCY1","FREQUENCY2","SPECTRUM"]
    ntuples["SYMBOL"] = ["F1","F2","Y"]
    ntuples[".NUCLEUS"] = ["UNKNOWN","UNKNOWN",""] #indirect and observe nuc
    ntuples["VAR_TYPE"] = ["INDEPENDENT","INDEPENDENT","DEPENDENT"]
    ntuples["VAR_FORM"] = ["AFFN","AFFN","ADSF"]
    ntuples["VAR_DIM"] = [z.shape[0], z.shape[1], z.shape[1]]
    ntuples["UNITS"] = ["PPM", "PPM", "ARBITRARY UNITS"]
    ntuples["FIRST"] = [ydata[0]*yscale, xdata[0]*xscale, zdata[0,0].real*zscale,]
    ntuples["LAST"] = [ydata[-1]*yscale, xdata[-1]*xscale, zdata[-1,-1].real*zscale]
    ntuples["MIN"] = [np.min(ydata)*yscale, np.min(xdata)*xscale, np.min(zdata.real)*zscale,]
    ntuples["MAX"] = [np.max(ydata)*yscale, np.max(xdata)*xscale, np.max(zdata.real)*zscale,]
    ntuples["FACTOR"] = [yscale, xscale, zscale,]

    block.update(ntuples)

    for i in range(len(ydata)):

        #print('$$printing page %s/%s'%(i+1,len(ydata)), file=sys.stderr)

        page = make_page()
        page["PAGE"] = " T1=%s"%(ydata[i]*yscale)
        page["FIRST"] = ntuples["FIRST"][:]
        page["FIRST"][0] = ydata[i]*yscale
        page["FIRST"] = ",".join(map(str,page["FIRST"]))

        newblock, _ = xy_to_dx( xdata, zdata[i].real,
                                xprec=0, yprec=0,
                                cols=80,
                                form=compression,
                                xsym=ntuples["SYMBOL"][1], ysym=ntuples["SYMBOL"][2])

        page["DATA TABLE"] = newblock["XYDATA"]

        pages.append(page)

    footer.update({"END NTUPLES":"nD NMR SPECTRUM"})

    for k in block:
        if type(block[k]) is list:
            block[k] = ",".join(map(str,block[k]))

    return block, pages, footer

def guess_dim_label(axis):

    axis = np.array(axis)
    center = axis[axis.size//2]
    axis_range = np.abs(axis[0] - axis[-1])

    if center < 10: return "1H"
    else: return "13C"


class jcamp_dx():

    #only one link block at top for now
    #can they be nested? how would numbering work?

    def __init__(self):

        self.blocks = []

        self.blocks.append(block("DX","LINK"))

    def add_block(self, b):
        b.block["BLOCK_ID"] = str(len(self.blocks))
        self.blocks.append(b)

    def link_blocks(self,a,b):

        if a is b: return

        #assume a, b are same data as in self.blocks
        if a.block["CROSS REFERENCE"] is None: a.block["CROSS REFERENCE"] = ""
        else: a.block["CROSS REFERENCE"] += "\n"

        if b.block["CROSS REFERENCE"] is None: b.block["CROSS REFERENCE"] = ""
        else: b.block["CROSS REFERENCE"] += "\n"


        if "JCAMP-CS" in b.block:
            a.block["CROSS REFERENCE"] += "STRUCTURE:BLOCK_ID=" +  b.block["BLOCK_ID"]
        else:
            a.block["CROSS REFERENCE"] += b.block["DATA TYPE"] + ":BLOCK_ID=" +  b.block["BLOCK_ID"]

        if "JCAMP-CS" in a.block:
            b.block["CROSS REFERENCE"] += "STRUCTURE:BLOCK_ID=" +  a.block["BLOCK_ID"]
        else:
            b.block["CROSS REFERENCE"] += a.block["DATA TYPE"] + ":BLOCK_ID=" +  a.block["BLOCK_ID"]


    def write(self):

        if len(self.blocks) == 2:
            self.blocks[1].block["BLOCK_ID"] = None
            self.blocks[1].write()
            return

        for b in self.blocks:
            b.write()

        if self.blocks[0].block["DATA TYPE"] == "LINK":
            print("##END=")


def load_nmrml(inputfile):
    #import xml.etree.ElementTree as ET
    #return ET.parse(inputfile)

    #manually parse misformatted nmrml
    with open(inputfile) as nmrml:
        filestring = nmrml.read()
    return filestring

#def get_nmrml_prefix(xmltree):
#    root = xmltree.getroot()
#    prefix = '{http://nmrml.org/schema}'
#    foundprefix = False
#    for r in root:
#        if prefix in r.tag:
#            foundprefix = True
#    if not foundprefix: prefix = ""
#    return prefix

def parse_nmrml_mol(filestring):

    #root = xmltree.getroot()
    #prefix = get_nmrml_prefix(xmltree)

    import xml.etree.ElementTree as ET
    import re
    import rdkit.Chem as Chem
    from rdkit.Geometry import Point3D

    structureblockstring = "<structure>.*?</structure>"
    structureblock = re.search(structureblockstring, filestring, re.MULTILINE + re.DOTALL)
    if structureblock is None:
        return
    #print(structureblock.group(0))
    structure = ET.fromstring(structureblock.group(0))
    prefix = ""


    #structure = root.find(prefix+'spectrumAnnotationList').find(prefix+'atomAssignment').find(prefix+'chemicalCompound').find(prefix+'structure')
    atoms = structure.find(prefix+'atomList')
    bonds = structure.find(prefix+'bondList')


    atomlabelmap = {}
    reversemap = {}
    atomblock = []
    is3d = False
    for i,a in enumerate(atoms):
    #id="a1" elementType="O" x="-1.8611" y="2.4646"/>
        #print(a.get('id'),a.get('elementType'),a.get('x'),a.get('y'),)
        atomlabelmap[a.get('id')] = i
        reversemap[i] = str(a.get('id'))
        atomblock.append([])
        atomblock[-1].append(i)
        atomblock[-1].append(a.get('elementType'))
        atomblock[-1].append(float(a.get('x')))
        atomblock[-1].append(float(a.get('y')))
        try:
            z = float(a.get('z'))
            atomblock[-1].append(z)
            if z != 0.0:
                is3d = True
        except:
            atomblock[-1].append(0.0)
        #print(atomblock[-1])

    bondblock = []
    for b in bonds:
    #atomRefs="a1 a10" order="1"
        #print(b.get('atomRefs'),b.get('order'))
        atom1, atom2 = b.get('atomRefs').replace(',',' ').split()
        bondblock.append([])
        bondblock[-1].append(atomlabelmap[atom1])
        bondblock[-1].append(atomlabelmap[atom2])
        bondblock[-1].append(int(b.get('order')))
        #print(bondblock[-1])



    mol = Chem.RWMol()
    conf = Chem.Conformer(len(atomblock))
    conf.Set3D(False)
    if is3d:
        conf.Set3D(True)

    for a in atomblock:
        atom = Chem.Atom(a[1])
        atom.SetProp('nmrml_atom_id', reversemap[a[0]])
        mol.AddAtom(atom)
        conf.SetAtomPosition(a[0], Point3D(a[2], a[3], a[4]))

    for b in bondblock:
        mol.AddBond(b[0],b[1],order=Chem.rdchem.BondType.values[b[2]])

    for a in mol.GetAtoms():
        #print(a.GetSymbol(), len(a.GetNeighbors()))
        if a.GetSymbol() == "N":
            if len(a.GetNeighbors()) == 4:
                #print("CHARGED N FOUND")
                a.SetFormalCharge(+1)
            if len(a.GetNeighbors()) == 3:
                b = a.GetBonds()
                for bi in b:
                    if bi.GetBondTypeAsDouble() == 2:
                        #print("CHARGED N FOUND")
                        a.SetFormalCharge(+1)
        if a.GetSymbol() == "O":
            if len(a.GetNeighbors()) == 1:
                b = a.GetBonds()[0]
                if b.GetBondTypeAsDouble() == 1:
                    #print("CHARGED O FOUND")
                    a.SetFormalCharge(-1)

    mol = mol.GetMol()
    mol.AddConformer(conf, assignId=True)
    Chem.SanitizeMol(mol)

    return mol

def parse_nmrml_assignments(xmltree, mol=None):

    try:
        peaklist = parse_1dnmrml_assignments(xmltree, mol=mol)
    except:
        peaklist = parse_2dnmrml_assignments(xmltree, mol=mol)

    return peaklist



def parse_1dnmrml_assignments(xmltree, mol=None):

    """
    parses atomAssignmentList to a list of lists
    outputs one row per peak, muliple rows per cluster
    atom ids are converted to atom index using atom.GetProp('nmrml_atom_id')
    """


    pattern = "<atomAssignmentList>.*?</atomAssignmentList>"
    assignments = re.search(pattern, xmltree, re.MULTILINE + re.DOTALL)
    if assignments is None:
        return
    assignments = ET.fromstring(assignments.group(0))

    atomlabelmap = {}
    if mol is not None:
        for a in mol.GetAtoms():
            if a.HasProp('nmrml_atom_id'):
                atomlabelmap[a.GetProp('nmrml_atom_id')] = a.GetIdx()
                atomlabelmap[a.GetSymbol() + a.GetProp('nmrml_atom_id')] = a.GetIdx()

    multiplets = {
                    'singlet':'s',
                    'doublet':"d",
                    'triplet':"t",
                    'quatruplet':"q",
                    'quartet':"q",
                    'quadruplet':"q",
                    'doublet of doublets':"dd",
                    'doublet of doublet of doublets':"ddd",
                    'doublet of doublet of doublet of doublets':'dddd',
                    'singlet':"s",
                    'quintet':"quint",
                    'doublet of triplets':"dt",
                    'triplet of douplets':"td",
                    'triplet of triplets':"tt",
                    'doublet of quartets':"dq",
                    'multiplet':"m",
                    'doublet of doublet of triplets':"ddt",
                    'doublet of triplet of doublets':"dtd",
                    'triplet of doublet of doublets':"tdd",
                    }

    #print("DEBUG ATOMS", atomlabelmap)
    peaklist = []
    for multiplet in assignments:
        atoms = multiplet.find('atoms').get('atomRefs').replace(',',' ').split()
        natoms = len(atoms)
        mult = multiplet.find('multiplicity').get('name').replace('feature','').strip().lower()
        mult = multiplets[mult] if mult in multiplets else 'NA'
        peaks = multiplet.find('peakList')
        for a in atoms:
            if peaks is None:
                peaklist.append([])
                peaklist[-1].append(atomlabelmap[a] if a in atomlabelmap else "NA")
                peaklist[-1].append(float(multiplet.get('center')))
                peaklist[-1].append(mult)
                peaklist[-1].extend(["NA","NA","NA"])
                continue

            for peak in peaks:
                peaklist.append([])
                peaklist[-1].append(atomlabelmap[a] if a in atomlabelmap else "NA")
                peaklist[-1].append(float(multiplet.get('center')))
                peaklist[-1].append(mult)
                peaklist[-1].append(float(peak.get('center')))
                peaklist[-1].append(float(peak.get('amplitude'))/natoms)
                peaklist[-1].append(float(peak.get('width')))

    return peaklist

def get_label_value(s):
    #atom string C1 -> string 1
    return "".join(c for c in str(s) if c.isdigit())

def parse_2dnmrml_assignments(xmltree, mol=None):

    """
    parses atomAssignmentList to a list of lists
    atom ids are converted to atom index using atom.GetProp('nmrml_atom_id')
    """

    pattern = "<atomAssignmentList>.*?</atomAssignmentList>"
    assignments = re.search(pattern, xmltree, re.MULTILINE + re.DOTALL)

    if assignments is None:
        return []
    assignments = ET.fromstring(assignments.group(0))

    header = ['Peak_ID','Spectral_dim_ID','Val','Entity_ID','Comp_index_ID','Comp_ID','Atom_ID','Details','Entry_ID','Spectral_peak_list_ID']
    peaklist = []
    peaklist.append(header)
    peakcounter = 1

    for multiplet in assignments:

        xppm = multiplet.get('dir_dim_center')
        yppm = multiplet.get('indir_dim_center')

        atoms = multiplet.find('atoms')
        xatoms = atoms.get('dir_dim_atomRefs').replace(',',' ').split()
        yatoms = atoms.get('indir_dim_atomRefs').replace(',',' ').split()
        nxatoms = len(xatoms)
        nyatoms = len(yatoms)

        #print(xppm, yppm, xatoms, yatoms, file=sys.stderr)

        for x, y in itertools.product(xatoms, yatoms):
            peaklist.append([peakcounter, 2, yppm, "?","?","?", y, "?","?","?",]) #vert dim
            peaklist.append([peakcounter, 1, xppm, "?","?","?", x, "?","?","?",]) #horiz dim
            peakcounter += 1

    return peaklist



def parse_nmrml_spectrum(filestring):

    import base64, zlib, re
    import xml.etree.ElementTree as ET

    #root = xmltree.getroot()
    #prefix = get_nmrml_prefix(xmltree)
    prefix = ""

    #acqu_par = root.find(prefix+'acquisition').find(prefix+'acquisition1D').find(prefix+'acquisitionParameterSet')
    #spec_block = root.find(prefix+'spectrumList').find(prefix+'spectrum1D').find(prefix+'spectrumDataArray')

    #print(filestring)
    acqu_block = re.search("<acquisition>.*?</acquisition>", filestring, re.MULTILINE + re.DOTALL)
    spec_block = re.search("<spectrumList>.*?</spectrumList>", filestring, re.MULTILINE + re.DOTALL)
    #flags = []

    #assume that each acquisition1D/acquisitionMultiD block has corresponding spectrum1D/spectrumMultiD block if both present
    #otherwise that only one of the above blocks exists

    a_blocks = []
    s_blocks = []


    if acqu_block:

        #print(acqu_block.group(0))

        acquisition = ET.fromstring(acqu_block.group(0))

        acquisition1d = acquisition.findall('acquisition1D')
        for acqu1d in acquisition1d:
            #print("$$1D acquisition block found")
            a_blocks.append(acqu1d)

        acquisitionnd = acquisition.findall('acquisitionMultiD')
        for acqund in acquisitionnd:
            #raise ValueError("$$nD acquisition block found, not supported")
            #continue
            a_blocks.append(acqund)


    if spec_block:

        spectrum = ET.fromstring(spec_block.group(0))

        spectrum1d = spectrum.findall('spectrum1D')
        for spec1d in spectrum1d:
            #print("$$1D spectrum block ound")
            s_blocks.append(spec1d)

        spectrumnd = spectrum.findall('spectrumMultiD')
        for specnd in spectrumnd:
            #raise ValueError("$$nD spectrum block found, not supported")
            #continue
            s_blocks.append(specnd)

    if len(a_blocks) == len(s_blocks):
        pass
    elif (a_blocks and not s_blocks) or (not a_blocks and s_blocks):
        pass
    elif len(a_blocks) == 1 and len(s_blocks) > 1:
        a_blocks = a_blocks * len(s_blocks)
    else:
        raise ValueError('could not parse nmrML acquisition/spectrum blocks')


    if (a_blocks and not s_blocks):
        #print("$$ only acquistion block found")
        for a in a_blocks:
            if a.tag == "acquisition1D":
                adic, adata = parse_nmrml_fid1d_block(a)
                #rint(adic, adata)
                if adata is not None:
                    yield '1DFID', adic, adata
            if a.tag == "acquisitionMultiD":
                adic, adata = parse_nmrml_fid2d_block(a)
                print(adic, adata)
                if adata is not None:
                    yield '2DFID', adic, adata

    if (s_blocks and not a_blocks):
        #print("$$ only spectrum block found")
        for s in s_blocks:
            if s.tag == "spectrum1D":
                sdic, sdata = parse_nmrml_spec1d_block(s)
                if sdata is not None:
                    yield '1DSPECTRUM', sdic, sdata
            if s.tag == "spectrumMultiD":
                sdic, sdata = parse_nmrml_spec2d_block(s)
                if sdata is not None:
                    yield '2DSPECTRUM', sdic, sdata

    if s_blocks and a_blocks:
        #print('$$ possible paired acq and spec blocks found')
        for a, s in zip(a_blocks, s_blocks):
            if a.tag == "acquisition1D" and s.tag == "spectrum1D":

                adic, adata = parse_nmrml_fid1d_block(a)
                sdic, sdata = parse_nmrml_spec1d_block(s)

                if adic['obs'] is not None and "unitsinhz" in sdic and sdic["unitsinhz"] == False:
                    sdic['car'] = sdic['car']/500 * adic['obs']
                    sdata[:,0] = sdata[:,0]*500/adic['obs']
                    if "C" in adic['label'] and adic['obs'] >= 250:
                        sdic['car'] *= 10.7084/42.577478518
                        sdata[:,0]  *= 10.7084/42.577478518
                    if "N" in adic['label'] and adic['obs'] >= 100:
                        sdic['car'] *= 4.316/42.577478518
                        sdata[:,0]  *= 4.316/42.577478518

                for k in adic: #acq params take precedence over fake spec parameters
                    if k in ['car','label','obs','sw','temp','groupdelay',] and adic[k] is not None:
                        sdic[k] = adic[k]

                if adata is not None:
                    yield '1DFID', adic, adata
                if sdata is not None:
                    yield '1DSPECTRUM', sdic, sdata

            if a.tag == "acquisitionMultiD" and s.tag == "spectrumMultiD":

                adic, adata = parse_nmrml_fid2d_block(a)
                sdic, sdata = parse_nmrml_spec2d_block(s)
                #print(adic)
                #print(sdic)

                for dim in [0, 1]:
                    if adic[dim]['obs'] is not None and "unitsinhz" in sdic and sdic[dim]["unitsinhz"] == False:
                        sdic[dim]['car'] = sdic[dim]['car']/500 * adic[dim]['obs']
                        if "C" in adic[dim]['label'] and adic[dim]['obs'] >= 250:
                            sdic[dim]['car'] *= 10.7084/42.577478518
                        if "N" in adic[dim]['label'] and adic[dim]['obs'] >= 100:
                            sdic[dim]['car'] *= 4.316/42.577478518

                    for k in adic[dim]: #acq params take precedence over fake spec parameters
                        if k in ['car','label','obs','sw','temp','groupdelay',] and adic[dim][k] is not None:
                            sdic[dim][k] = adic[dim][k]

                #print(adic)
                #print(sdic)

                if adata is not None:
                    yield '2DFID', adic, adata
                if sdata is not None:
                    yield '2DSPECTRUM', sdic, sdata



def parse_nmrml_spec1d_block(xmlblock):

    s = xmlblock

    if s.tag == 'spectrum1D':
        #print('$$reading 1d spec')

        try:
            npoints = s.get('numberOfDataPoints')

            sdata = s.find('spectrumDataArray')

            compressed = sdata.get('compressed')
            encode = sdata.get('encodedLength')
            byteformat = sdata.get('byteFormat')
            #print(compressed, encode, byteformat)
            #spec is assumed to be interleaved  x,y
            #y data only is also mentioned in spec...
            spec = parse_nmrml_blob(sdata.text, compressed, byteformat, npoints)

            #assume 500 Mhz
            sfrq = 500.0
            #guess units
            sw = np.abs(np.diff(spec[[0,-1],0]).item())
            if sw > 250: #in hz
                car = spec[spec.shape[0]//2,0]
                sw = sw
                spec[:,0] /= sfrq #hz to ppm
                unitsinhz = True
            else: #in ppm
                car = spec[spec.shape[0]//2,0] * sfrq
                sw = sw * sfrq
                unitsinhz = False

            udic = {'complex':False,'freq':True,'encoding':'direct','time':False,
                    'car':car,
                    'label':None,
                    'obs':sfrq,
                    'size':spec.shape[0],
                    'sw':sw,
                    'temp':None,
                    'groupdelay':None,
                    'unitsinhz':unitsinhz}

            return udic, spec

        except:
            return {'complex':False,'freq':True,'encoding':'direct','time':False,}, None
    else:
        return {'complex':False,'freq':True,'encoding':'direct','time':False,}, None



def parse_nmrml_fid1d_block(xmlblock):

    import numpy as np

    a = xmlblock

    if a.tag == 'acquisition1D':
        #print('$$reading 1d fid')
        acparamtag = 'acquisitionParameterSet1D'
        if a.find('acquisitionParameterSet1D') is None:
            acparamtag = 'acquisitionParameterSet'
        dirdimparamsettag = 'DirectDimensionParameterSet'
        if a.find(acparamtag).find('DirectDimensionParameterSet') is None:
            dirdimparamsettag = 'directDimensionParameterSet'

        try:
            temp = float(a.find(acparamtag).find('sampleAcquisitionTemperature').get('value'))
            if "kelvin" in a.find(acparamtag).find('sampleAcquisitionTemperature').get('unitName'):
                if temp > 200:
                    temp = temp - 273.15
        except:
            temp = None

        try:
            groupdelay = float(a.find(acparamtag).find('groupDelay').get('value'))
        except:
            groupdelay = None

        try:
            npoints = int(a.find(acparamtag).find(dirdimparamsettag).get('numberOfDataPoints'))
        except:
            npoints = None

        try:
            label =  a.find(acparamtag).find(dirdimparamsettag).find('acquisitionNucleus').get('name')
            if 'hydrogen' in label: label = "1H"
            if 'carbon' in label: label = "13C"
            if 'nitrogen' in label: label = "15N"
            if 'phos' in label: label = "31P"
            if 'flourine' in label: label = "19F"
        except:
            label = "NA"

        #assume units cannot be trusted...
        sfrq = None
        try:
            field = float(a.find(acparamtag).find(dirdimparamsettag).find('effectiveExcitationField').get('value'))
            #print(field)
            if float(field) < 1500:
                sfrq =  field
            if float(field) > 1e6:
                sfrq =  field / 1e6
        except:
            pass

        try:
            carrier = float(a.find(acparamtag).find(dirdimparamsettag).find('irradiationFrequency').get('value'))
            #print(carrier)
            if float(carrier) < 1500:
                sfrq =  carrier
            if float(carrier) > 1e6:
                sfrq =  carrier / 1e6
        except:
            pass

        try:
            sw = float(a.find(acparamtag).find(dirdimparamsettag).find('sweepWidth').get('value'))
            if "parts per million" in a.find(acparamtag).find(dirdimparamsettag).find('sweepWidth').get('unitName'):
                sw = sw * sfrq
        except:
            sw = None

        udic = {'complex':True,'freq':False,'encoding':'direct','time':True,
                'car':None,
                'label':label,
                'obs':sfrq,
                'size':None,
                'sw':sw,
                'temp':temp,
                'groupdelay':groupdelay,}


        try:
            fid = a.find('fidData')
            compressed = fid.get('compressed')
            byteformat = fid.get('byteFormat')
            #fid is assumed to be interleaved y.real,y.imag
            spec = parse_nmrml_blob(fid.text, compressed, byteformat, npoints)
            udic['size'] = len(spec)
            xaxis = np.linspace(0,1/udic['sw']*udic['size'],udic['size'])
            return udic, np.column_stack((xaxis,spec[:,0],spec[:,1])) #x, r, i

        except:
            return udic, None
    else:
        return {'complex':True,'freq':False,'encoding':'direct','time':True,}, None



def parse_nmrml_fid2d_block(xmlblock):

    import numpy as np

    a = xmlblock

    if a.tag == 'acquisitionMultiD':
        #print('$$reading multiD fid')
        acparamtag = 'acquisitionParameterSet1D'
        if a.find('acquisitionParameterSetMultiD') is None:
            acparamtag = 'acquisitionParameterSet'
        dirdimparamsettag = 'DirectDimensionParameterSet'
        if a.find(acparamtag).find('DirectDimensionParameterSet') is None:
            dirdimparamsettag = 'directDimensionParameterSet'

        try:
            temp = float(a.find(acparamtag).find('sampleAcquisitionTemperature').get('value'))
            if "kelvin" in a.find(acparamtag).find('sampleAcquisitionTemperature').get('unitName'):
                if temp > 200:
                    temp = temp - 273.15
        except:
            temp = None

        try:
            groupdelay = float(a.find(acparamtag).find('groupDelay').get('value'))
        except:
            groupdelay = None

        try:
            npoints = int(a.find(acparamtag).find(dirdimparamsettag).get('numberOfDataPoints'))
        except:
            npoints = None

        try:
            label =  a.find(acparamtag).find(dirdimparamsettag).find('acquisitionNucleus').get('name')
            if 'hydrogen' in label: label = "1H"
            if 'carbon' in label: label = "13C"
            if 'nitrogen' in label: label = "15N"
            if 'phos' in label: label = "31P"
        except:
            label = "NA"

        #assume units cannot be trusted...
        sfrq = None
        try:
            field = float(a.find(acparamtag).find(dirdimparamsettag).find('effectiveExcitationField').get('value'))
            #print(field)
            if float(field) < 1500:
                sfrq =  field
            if float(field) > 1e6:
                sfrq =  field / 1e6
        except:
            pass

        try:
            carrier = float(a.find(acparamtag).find(dirdimparamsettag).find('irradiationFrequency').get('value'))
            #print(carrier)
            if float(carrier) < 1500:
                sfrq =  carrier
            if float(carrier) > 1e6:
                sfrq =  carrier / 1e6
        except:
            pass

        try:
            sw = float(a.find(acparamtag).find(dirdimparamsettag).find('sweepWidth').get('value'))
            if "parts per million" in a.find(acparamtag).find(dirdimparamsettag).find('sweepWidth').get('unitName'):
                sw = sw * sfrq
        except:
            sw = None


        udic = {'ndim':2,
                0:{ 'complex':True,'freq':False,'encoding':'unknown','time':True,
                    'car':None,
                    'label':"13C?",
                    'obs':sfrq * 10.7084/42.577478518,
                    'size':None,
                    'sw':sw,
                    'temp':temp,
                    'groupdelay':0 if groupdelay else None,},
                1:{'complex':True,'freq':False,'encoding':'direct','time':True,
                    'car':None,
                    'label':"1H",
                    'obs':sfrq,
                    'size':None,
                    'sw':sw,
                    'temp':temp,
                    'groupdelay':groupdelay,},
                }

        try:
            #no examples of 2D/multiD FID, so this should always error...
            raise ValueError('2d fid data not supported')

        except:
            #return only the parsed udic
            return udic, None
    else:
        return {'complex':True,'freq':False,'encoding':'direct','time':True,}, None



def parse_nmrml_spec2d_block(xmlblock):

    import numpy as np

    s = xmlblock

    if s.tag == 'spectrumMultiD':
        #print('$$reading 2d spec')

        try:
            npoints = s.get('numberOfDataPoints')

            sdata = s.find('spectrumDataArray2dIntensities')

            compressed = sdata.get('compressed')
            encode = sdata.get('encodedLength')
            byteformat = sdata.get('byteFormat')
            #z data is not interleaved
            if byteformat == 'complex128': byteformat = 'float64'

            specz = parse_nmrml_blob(sdata.text, compressed, byteformat, npoints,
                                    interleaved=False)

            sdata = s.find('spectrumDataArray2dDirectDimensionF2')

            compressed = sdata.get('compressed')
            encode = sdata.get('encodedLength')
            byteformat = sdata.get('byteFormat')
            if byteformat == 'complex128': byteformat = 'float64'

            specx = parse_nmrml_blob(sdata.text, compressed, byteformat, None,
                                    interleaved=False)


            sdata = s.find('spectrumDataArray2dIndirectDimensionF1')

            compressed = sdata.get('compressed')
            encode = sdata.get('encodedLength')
            byteformat = sdata.get('byteFormat')
            if byteformat == 'complex128': byteformat = 'float64'

            specy = parse_nmrml_blob(sdata.text, compressed, byteformat, None,
                                    interleaved=False)

            #assume 500 mhz for now

            udic = {'ndim':2,
                    0:{
                        'complex':False,'freq':True,'encoding':'direct','time':False,
                        'car':specy[specy.size//2] * 500 * 10.7084/42.577478518,
                        'label':"13C?",
                        'obs':500 * 10.7084/42.577478518,
                        'size':specy.size,
                        'sw':(specy[0] - specy[-1]) * 500 * 10.7084/42.577478518,
                        'temp':None,
                        'groupdelay':None,
                        },
                    1:{
                        'complex':False,'freq':True,'encoding':'direct','time':False,
                        'car':specx[specx.size//2] * 500,
                        'label':"1H",
                        'obs':500,
                        'size':specx.size,
                        'sw':(specx[0] - specx[-1]) * 500,
                        'temp':None,
                        'groupdelay':None,
                        },
                    }

            specz = specz.reshape(specy.size, specx.size)

            return udic, specz

        except:
            return {'complex':False,'freq':True,'encoding':'direct','time':False,}, None
    else:
        return {'complex':False,'freq':True,'encoding':'direct','time':False,}, None
    return


def parse_nmrml_blob(s, compressed='False', byteformat="complex128", points=1024*32, interleaved=True):
    #mark nmrml is len(xy pairs), old xml is len(x) + len(y)
    #points not used

    import base64, zlib

    data = base64.b64decode(s)

    if compressed.lower() == "true":
        data = zlib.decompress(data)

    byteformat = byteformat.lower()

    dataarr = np.frombuffer(data, byteformat)

    #some example nmrml are complex64 (2xfloat32) but declared as complex128...
    if np.any(np.abs(dataarr.real) > 1e40) or np.any(np.abs(dataarr.imag) > 1e40):
        dataarr = np.frombuffer(data, 'complex64')

    if interleaved:
        x, y = dataarr.real, dataarr.imag
        if np.all(y == 0):
            x, y = dataarr[0::2], dataarr[1::2]
        return np.column_stack((x, y))
    else:
        return dataarr

def parse_nmrml_metadata(xmltree):

    import re
    import xml.etree.ElementTree as ET

    metadata = {'ref':None, 'solvent':None, 'name':None, 'reference':None, 'reftype':None}

    lock = re.search("<fieldFrequencyLock\s*fieldFrequencyLockName=\"(.*?)\".*?>", xmltree)
    ref = re.search("<chemicalShiftStandard.?\s*name=\"(.*?)\".*?>", xmltree)

    if lock:
        metadata['solvent'] = lock.group(1)
    if ref:
        metadata['ref'] = ref.group(1)

    name = re.search("<identifier.*?name=\"(.*?)\".*?>", xmltree)
    reference = re.search("<NPMRD_REFERENCE.*?value=\"(.*?)\".*?>", xmltree)
    reftype = re.search("<NPMRD_REFERENCE_TYPE.*?value=\"(.*?)\".*?>", xmltree)

    if name:
        metadata['name'] = name.group(1)
    if reference:
        metadata['reference'] = reference.group(1)
    if reftype:
        metadata['reftype'] = reftype.group(1)

    return metadata

def nmrmltojcamp(nmrmlfile):

    import rdkit.Chem as Chem
    import nmrglue as ng

    filestring = load_nmrml(nmrmlfile)

    m = parse_nmrml_metadata(filestring)

    jcampmeta = {"ORIGIN":"NP-MRD", "OWNER":"NP-MRD",
                 "TITLE":m['name'],}

    if m['reference'] and m['reftype']:
        jcampmeta["SOURCE REFERENCE"] = "%s: %s"%(m['reftype'],m['reference'])
    elif m['reference']:
        jcampmeta["SOURCE REFERENCE"] = "%s"%(m['reference'])
    else:
        jcampmeta["SOURCE REFERENCE"] = None

    jcamp = jcamp_dx()
    currblock = jcamp.blocks[0] #link block
    currblock.block.update(jcampmeta)

    mol = parse_nmrml_mol(filestring)
    if mol is not None:
        currblock = block("CS")
        currblock.block.update(jcampmeta)
        currblock.block.update(make_mol(Chem.MolToMolBlock(mol), ispath=False))
        jcamp.add_block(currblock)


    for spectype, udic, spec in parse_nmrml_spectrum(filestring):

        #print(spectype)
        #print(udic)
        #print(specmeta)
        #print(spec)

        if spectype == "1DFID":
            specmeta = {".SOLVENT NAME":m['solvent'], ".OBSERVE NUCLEUS":udic['label'],
                        ".OBSERVE FREQUENCY":udic['obs']}
            currblock = block("DX","NMR FID")
            currblock.block.update(jcampmeta)
            currblock.block.update(specmeta)
            b, p, f = make_fid(spec)
            currblock.block.update(b)
            currblock.pages = p
            oldfooter = currblock.footer
            currblock.footer = f
            currblock.footer.update(oldfooter)

        if spectype == "1DSPECTRUM":
            specmeta = {".SOLVENT NAME":m['solvent'], ".OBSERVE NUCLEUS":udic['label'],
                        ".OBSERVE FREQUENCY":udic['obs']}
            currblock = block("DX","NMR SPECTRUM")
            currblock.block.update(jcampmeta)
            currblock.block.update(specmeta)
            currblock._refvalues = ["INTERNAL", m['ref'] or "NA", "NA", "NA"]
            currblock.block.update(make_spectrum(spec))
            blockdic=currblock.block
            reflist = currblock._refvalues
            if ("C" in blockdic[".OBSERVE NUCLEUS"] or "H" in blockdic[".OBSERVE NUCLEUS"]):
                testcpd = reflist[1].upper()
                if "TMS" in testcpd or "DSS" in testcpd or "TSP" in testcpd or "SIL" in testcpd:
                    if not reflist[3] or reflist[3] == "NA":
                        reflist[3] = 0.0
            if reflist[3] and reflist[3] != "NA":
                ppm = reflist[3]
                first = float(blockdic["FIRSTX"])
                last  = float(blockdic["LASTX"])
                npoints = int(blockdic["NPOINTS"])
                reflist[2] = "%.2f"%(interp1d(np.linspace(first, last, npoints), np.arange(npoints), fill_value="extrapolate")(ppm))
            blockdic[".SHIFT REFERENCE"] = ",".join(map(str,reflist))


        if spectype == "2DFID":
            raise ValueError('2d fid not supported')

        if spectype == "2DSPECTRUM":
            lastd = max((k for k in udic if k != 'ndim'))
            specmeta = {".SOLVENT NAME":m['solvent'], ".OBSERVE NUCLEUS":udic[lastd]['label'],
                        ".OBSERVE FREQUENCY":udic[lastd]['obs']}
            currblock = block("DX","nD NMR SPECTRUM")
            currblock.block.update(jcampmeta)
            currblock.block.update(specmeta)
            currblock._refvalues = ["INTERNAL", m['ref'] or "NA", "NA", "NA"]
            b, p, f = make_nmrml_2d_spec(m, udic, spec)
            currblock.block.update(b)
            currblock.pages = p
            oldfooter = currblock.footer
            currblock.footer = f
            currblock.footer.update(oldfooter)
            #raise ValueError('2d spectrum not supported')

        jcamp.add_block(currblock)

    p = parse_nmrml_assignments(filestring, mol)
    #get the first instance of .OBSERVE FREQUENCY, .OBSERVE NUCLEUS
    tmp_meta = {".OBSERVE FREQUENCY":"UNKNOWN",
                ".OBSERVE NUCLEUS":"UNKNOWN"}
    for blk in jcamp.blocks:
        try:
            obs = blk.block[".OBSERVE FREQUENCY"]
            nuc = blk.block[".OBSERVE NUCLEUS"]
            if obs == "UNKNOWN" or nuc == "UNKNOWN":
                continue
            else:
                tmp_meta[".OBSERVE FREQUENCY"] = obs
                tmp_meta[".OBSERVE NUCLEUS"] = nuc
        except:
            continue

    if p:
        if len(p[0]) != 10: #is 1d data
            pktbl = make_peaktable(p)
            if pktbl:
                currblock = block("DX","NMR PEAK TABLE")
                currblock.block.update(jcampmeta)
                currblock.block.update(pktbl)
                currblock.block.update(tmp_meta)
                jcamp.add_block(currblock)

            asgntbl = make_assignments(p)
            if asgntbl:
                currblock = block("DX","NMR PEAK ASSIGNMENTS")
                currblock.block.update(jcampmeta)
                currblock.block.update(asgntbl)
                currblock.block.update(tmp_meta)
                jcamp.add_block(currblock)
        else: #is 2d data
            pktbl = make_2d_assignments(p)
            if pktbl:
                currblock = block("DX","NMR PEAK ASSIGNMENTS")
                currblock.block.update(jcampmeta)
                currblock.block.update(pktbl)
                currblock.block.update(tmp_meta)
                jcamp.add_block(currblock)

    jcamp.write()

    return

def split_2d_label(s):
    return "".join([c for c in s if c.isdigit()])


def parse_2d_peak_list(f):

    #        csv based on bmrb: Peak_ID, Atom_ID, Val, Spectral_dim_ID
    #        csv from nmrpred: symbmol, id, symbol, id, ppm, ppm

    """
    new  version
    Peak_ID,Spectral_dim_ID,Val,Entity_ID,Comp_index_ID,Comp_ID,Atom_ID,Details,Entry_ID,Spectral_peak_list_ID
    1,1,6.2,?,?,?,H46,?,?,?
    1,2,6.2,?,?,?,H47,?,?,?
    """

    with open(f) as csvfile:
        reader = csv.reader(csvfile)
        data = []
        for line in reader:
            if line[0].startswith("#"): continue
            if line[0].startswith("Peak"): continue
            data.append(line)


    #return dict with peak_id:[id1, id2, ppm1, ppm2]
    #assignments may be duplicated: peak 1 -> 13c, 1H(ch2), 1H(ch2)
    #need to fix...
    peak_list = {}

    if len(data[0]) == 4:
        for line in data:
            try:
                peak_id = int(line[0])
            except:
                continue
            try:
                atom_id = int(split_2d_label(line[1]))
            except:
                atom_id = "NA"
            try:
                ppm = float(line[2])
            except:
                continue
            try:
                #use as offset
                dim = int(line[3]) #1 or 2
                if dim == 1: dim = 0
                if dim == 2: dim = 1
            except:
                continue
            if peak_id not in peak_list:
                peak_list[peak_id] = ["NA", "NA", "NA", "NA"]
            peak_list[peak_id][2+dim] = atom_id
            peak_list[peak_id][0+dim] = ppm
            print(peak_id, atom_id, ppm, dim)


    elif len(data[0]) == 6:
        for i, line in enumerate(data):
            peak_id = i
            try:
                atom1_id = int(line[1])
            except:
                atom1_id = "NA"
            try:
                atom2_id = int(line[3])
            except:
                atom2_id = "NA"
            try:
                ppm1 = float(line[4])
            except:
                ppm1 = "NA"
            try:
                ppm2 = float(line[5])
            except:
                ppm2 = "NA"
            peak_list[peak_id] = [atom1_id, atom2_id, ppm1, ppm2]
        pass



    elif len(data[0]) == 10:
        for line in data:
            try:
                peak_id = int(line[0])
            except:
                continue
            try:
                atom_id = int(split_2d_label(line[6]))
            except:
                atom_id = "NA"
            try:
                ppm = float(line[2])
            except:
                continue
            try:
                #use as offset
                dim = int(line[1]) #1 or 2
                if dim == 1: dim = 0
                if dim == 2: dim = 1
            except:
                continue
            if peak_id not in peak_list:
                peak_list[peak_id] = ["NA", "NA", "NA", "NA"]
            peak_list[peak_id][2+dim] = atom_id
            peak_list[peak_id][0+dim] = ppm
            #print(peak_id, atom_id, ppm, dim)

    return peak_list


def make_2d_assignments(data, table_format="XYA", labels=["X"], units=["PPM"], ):

    #data contains header

    block = {}

    if len(data)-1 < 1:
        return block

    data = data[1:]

    if not len(data[0]) == 10:
        return block

    block["DATA CLASS"] = "PEAK ASSIGNMENTS"
    block["NPOINTS"] = str(len(data))

    for label, unit in zip(labels, units):
        block[label + "UNITS"] = unit

    block["PEAK ASSIGNMENTS"] = "(%s)"%table_format

    #print(data)
    for row in data:
        row = list(map(str,row))
        row = [row[2], "", get_label_value(row[6])]

        try:
            row[table_format.index("A")] = "<%s>"%int(float(row[table_format.index("A")]))
        except:
            row[table_format.index("A")] = "<%s>"%("NA")

        block["PEAK ASSIGNMENTS"] += "\n(%s)"%(", ".join(row))


    return block


if __name__ == "__main__":

    import sys

    helpstr = """
    makes jcamp file from certain inputs

    python createjcamp.py [options...] > newfile.jdx


    --fromnmrml NMRML   converts nmrml file (no other arguments)
                        **2d peak lists currently ignored


    --title TITLE       TITLE for current BLOCK
    --origin STRING     ORIGIN
    --owner STRING      OWNER
    --link INDEX        add LINK to previously added BLOCK

    --block TYPE        append new BLOCK

    --block STRUCTURE --file PATH     mol/sdf file

    --block 1DSPECTRUM --file PATH [csv|tsv|json|bruk|var]

        csv/tsv/json with x,y
        path to bruker folder with "1r", "procs"
        path to varian folder with "fid", "procpar"

    --block 1DFID --file PATH [csv|tsv|bruk|var]

        csv/tsv with x,R,I
        path to bruker folder with "fid", "acqus"
        path to varian folder with "fid", "procpar"

    --block 1DPEAKS --file PATH [csv|tsv|json]

        csv/tsv with one line per atom:
        atom index, shift, multiplicty, peak position(s), peak height(s)

    --block 2DPEAKS --file PATH [json]

        x, y, z(int) is output

        json file:{
                    "0": {
                            "ypos": 2.501205639033179,
                            "xpos": 159.14414932308614,
                            "ylw": 0.0,
                            "xlw": 0.3319721506851181,
                            "int": 87247.21875,
                            "vol": 247822.4375
                            },
                     "1": { ...
                            },

    --block ASSIGNMENTS --file PATH [csv|tsv]

        csv/tsv with one line per atom:
        atom index, shift, multiplicty, peak position(s), peak height(s)

    --block 2DSPECTRUM --file PATH [json|bruk|var]

        json with x,y axis and z unraveled intensities
        path to bruker folder with "1rr", "acqus" "acqu2s"
        path to varian folder with "fid", "procpar"

    --block 2DFID --file PATH [bruk|var]

        path to bruker "ser", "acqus" "acqu2s"
        path to varian folder with "fid", "procpar"

    --block 2DASSIGNMENTS --file PATH [csv]

        csv based on bmrb: Peak_ID, Atom_ID, Val, Spectral_dim_ID
                            with Spectral_dim_ID 1 (direct) or 2 (indirect)
        csv from nmrpred: symbol1, id1, symbol2, id2, ppm1, ppm2

    --block 2DPEAKS --file PATH [json]

        json only for now with format
            0:
                ypos:   7.846505701751855
                xpos:   139.9819615529459
                ylw:    0.22559562374783404
                xlw:    0.3952258765770864
                int:    595142.2047629794
                vol:    100956932.84164487
            1:
                ...
        peaks with xlw or ylw == 0 are skipped
        vol not used

    for current --block 1DSPECTRUM/2DSPECTRUM/1DFID/2DFID:

        --reftype [INTERNAL|EXTERNAL]   .SHIFT REFERENCE
        --refcpd STRING                 .SHIFT REFERENCE/.SOLVENT REFERENCE
        --refppm VALUE                  .SHIFT REFERENCE/.SOLVENT REFERENCE
        --spectype STRING               .PULSE SEQUENCE
        --mode SIMULTANEOUS|SEQUENTIAL|SINGLE       .ACQUISITION MODE
        --delay VALUE VALUE                         .DELAY (us)

    other metadata for current BLOCK:

    --desc STRING       SAMPLE DESCRIPTION

    --frq VALUE         .OBSERVE FREQUENCY (megahertz)
    --nuc STRING        .OBSERVE NUCLEUS (eg --nuc 1H)
        or
    --nuc STRING STRING .NUCLEUS (eg --nuc 1H 13C)
                        direct dimension first
    --sol STRING        .SOLVENT NAME
    --temp VALUE        TEMPERATURE (celsius)
    --ph VALUE          $PH
    --mp VALUE          MP
    --bp VALUE          BP
    --ref VALUE         SOURCE REFERENCE
    --comment STRING    $COMMENTS (could be used for other comments)

    --frq, --nuc, --temp, --sol, --nuc, --mode, --delay:
    extracted from bruk/var parameters and cannot be overwritten


    examples:

    python createjcamp.py --title "TEST FILE" \
    --block STRUCTURE   --file structure.mol                --title "STRUCTURE" \
    --block 1DSPECTRUM  --file example_1h_spectrum.txt csv  --title "SPECTRUM"      --frq 500 --nuc 1H --refcpd DSS --refppm 0 \
    --block 1DPEAKS     --file example_1h_peaklist.txt csv  --title "PEAKS"         --frq 500 --nuc 1H --link 1 \
    --block ASSIGNMENTS --file example_1h_peaklist.txt csv  --title "ASSIGNMENTS"   --frq 500 --nuc 1H --link 2 \
    > output.jdx

    python createjcamp.py --title "FROM BRUKER" --block 1DSPECTRUM --file ./nmr.fid/pdata/1/ bruk

    python createjcamp.py --fromnmrml 226_NP0001015_28.nmrML

    """

    if sys.argv[1] == '--help':
        print(helpstr.strip())
        sys.exit(0)

    filetypes = ['STRUCTURE',
                '1DSPECTRUM','1DFID',
                'ASSIGNMENTS','1DPEAKS',
                '2DSPECTRUM','2DFID','2DASSIGNMENTS',"2DPEAKS"]

    fileformats = ['csv','tsv','json','nmrml','var','bruk',]
    args = sys.argv[1:]

    now = datetime.datetime.today()
    currdate = now.strftime('%y/%m/%d')
    currtime = now.strftime('%H:%M:%S')
    currlongdate = now.strftime('%Y/%m/%d %H:%M:%S %z')



    if "--fromnmrml" in args:
        argidx = args.index("--fromnmrml") + 1
        print('converting nmrml file', args[argidx], file=sys.stderr,)
        nmrmltojcamp(args[argidx])
        sys.exit(0)



    jcamp = jcamp_dx()
    currblock = jcamp.blocks[0]
    currblocktype = "LINK"

    specmax = None #can scale the peaks if spectrum file added first

    for i in range(len(args)):


        if args[i] == "--block":

            currblocktype = args[i+1]

            if currblocktype not in filetypes: raise ValueError('must be one of %s'%(str(filetypes)))

            if currblocktype == "STRUCTURE":
                currblock = block("CS")

            if currblocktype == "1DSPECTRUM":
                currblock = block("DX","NMR SPECTRUM")
                currblock._refvalues = ["INTERNAL","UNKNOWN",0,0]

            if currblocktype == "1DFID":
                currblock = block("DX","NMR FID")

            if currblocktype == "ASSIGNMENTS":
                currblock = block("DX","NMR PEAK ASSIGNMENTS")

            if currblocktype == "2DASSIGNMENTS":
                currblock = block("DX","NMR 2D PEAK ASSIGNMENTS")

            if currblocktype == "1DPEAKS":
                currblock = block("DX","NMR PEAK TABLE")

            if currblocktype == "2DPEAKS":
                currblock = block("DX","nD NMR PEAK TABLE")

            if currblocktype == "2DFID":
                currblock = block("DX","nD NMR FID")

            if currblocktype == "2DSPECTRUM":
                currblock = block("DX","nD NMR SPECTRUM")
                currblock._refvalues = ["INTERNAL","UNKNOWN",0,0]

            jcamp.add_block(currblock)

        if args[i] == "--file":

            if currblocktype == "STRUCTURE":
                print('adding mol file', args[i+1], file=sys.stderr,)
                currblock.add_mol(args[i+1]) # a mol file

            if currblocktype == "1DSPECTRUM":
                fformat = 'csv'
                print('adding 1d spectrum', args[i+1], file=sys.stderr,)
                if args[i+2] in fileformats: fformat = args[i+2]
                #if fformat in ['bruk']: raise ValueError('file format not supported for spectrum')
                currblock.add_1d_spectrum(args[i+1], fformat) # a spectrum in csv/tsv/json x,y format, or nmrml
                specmax = currblock._specmax

            if currblocktype == "1DFID":
                fformat = 'csv'
                print('adding 1d fid', args[i+1], file=sys.stderr,)
                if args[i+2] in fileformats: fformat = args[i+2]
                if fformat in ['json','nmrml',]: raise ValueError('file format not supported for fid')
                currblock.add_1d_fid(args[i+1], fformat) # a fid in csv/tsv x,r,i format

            if currblocktype == "ASSIGNMENTS":
                fformat = 'csv'
                print('adding 1d assignments', args[i+1], file=sys.stderr,)
                if args[i+2] in fileformats: fformat = args[i+2]
                if fformat in ['json','nmrml']: raise ValueError('file format not supported for assignments')
                currblock.add_assignments(args[i+1], fformat) # csv/tsv (atom index, shift, mutliplicity, other(ignored))

            if currblocktype == "2DASSIGNMENTS":
                fformat = 'csv'
                print('adding 2d assignments', args[i+1], file=sys.stderr,)
                if args[i+2] in fileformats: fformat = args[i+2]
                if fformat in ['json','nmrml']: raise ValueError('file format not supported for 2d assignments')
                currblock.add_2dassignments(args[i+1], fformat) # csv/tsv (atom index, shift, mutliplicity, other(ignored))

            if currblocktype == "1DPEAKS":
                fformat = 'csv'
                print('adding 1d peak list', args[i+1], file=sys.stderr,)
                if args[i+2] in fileformats: fformat = args[i+2]
                if fformat in ['nmrml']: raise ValueError('file format not supported for peaks')
                currblock.add_peaktable(args[i+1], fformat) # csv/tsv (atom, shift, mult, x, y)

            if currblocktype == "2DPEAKS":
                fformat = 'json'
                print('adding 2d peak list', args[i+1], file=sys.stderr,)
                if args[i+2] in fileformats: fformat = args[i+2]
                if fformat in ['csv','tsv','nmrml']: raise ValueError('file format not supported for 2d peaks')
                currblock.add_2dpeaktable(args[i+1], fformat)

            if currblocktype == "2DFID":
                print('adding 2d fid', args[i+1], file=sys.stderr,)
                if args[i+2] in fileformats: fformat = args[i+2]
                if fformat in ['csv','tsv','json','nmrml']: raise ValueError('file format not supported for 2d fid')
                currblock.add_2dfid(args[i+1], fformat)

            if currblocktype == "2DSPECTRUM":
                print('adding 2d spectrum', args[i+1], file=sys.stderr,)
                if args[i+2] in fileformats: fformat = args[i+2]
                if fformat in ['csv','tsv',]: raise ValueError('file format not supported for 2d spectrum')
                currblock.add_2dspectrum(args[i+1], fformat)


        if currblocktype == "ASSIGNMENTS":
            if args[i] == "--jassigntbl":
                print('adding coupling constants from assignment table', args[i+1], file=sys.stderr,)
                #assignment table is the one used as input for nmrpred
                currblock.add_coup_from_assigntable(args[i+1])


        if args[i] == "--title":
            currblock.set_param("TITLE",args[i+1])

        if args[i] == "--desc":
            currblock.set_param("SAMPLE DESCRIPTION",args[i+1])

        if args[i] == "--frq":
            if currblock.block[".OBSERVE FREQUENCY"] == "UNKNOWN":
                currblock.set_param(".OBSERVE FREQUENCY",args[i+1])

        if args[i] == "--nuc":

            if (currblock.block[".OBSERVE NUCLEUS"] == "UNKNOWN"):
                currblock.set_param(".OBSERVE NUCLEUS", args[i+1])

            if currblocktype.startswith("2D"):
                #--nuc 1H 13C for 1H in direct dimension
                nuc_dir = args[i+1]
                nuc_indir = args[i+2] if not args[i+2].startswith("--") else "UNKNOWN"

                try:
                    if (currblock.block[".NUCLEUS"] == "UNKNOWN") or (currblock.block[".NUCLEUS"] == "UNKNOWN,UNKNOWN,"):
                        currblock.set_param(".NUCLEUS",",".join(map(str,[nuc_indir, nuc_dir,""])))
                except Exception as e:
                    #probably assignments
                    pass



        if args[i] == "--sol":
            if currblock.block[".SOLVENT NAME"] is None:
                currblock.set_param(".SOLVENT NAME",args[i+1])

        if currblocktype in ["1DSPECTRUM", "2DSPECTRUM", "1DFID", "2DFID"]:
            if args[i] == "--reftype":
                if args[i+1] not in ("INTERNAL", "EXTERNAL"):
                    raise ValueError()
                currblock._refvalues[0] = args[i+1]
            if args[i] == "--refcpd":
                currblock._refvalues[1] = args[i+1]
            if args[i] == "--refppm":
                currblock._refvalues[3] = args[i+1]
                currblock.set_param(".SOLVENT REFERENCE",args[i+1])
            if args[i] == "--spectype":
                currblock.set_param(".PULSE SEQUENCE",args[i+1])
            if args[i] == "--mode":
                if currblock.block[".ACQUISITION MODE"] is None:
                    currblock.set_param(".ACQUISITION MODE",args[i+1])
            if args[i] == "--delay":
                if currblock.block[".DELAY"] is None:
                    currblock.set_param(".DELAY",tuple(map(float,args[i+1:i+3])))

        if args[i] == "--link":
            jcamp.link_blocks(currblock,jcamp.blocks[int(args[i+1])])

        #other meta data
        if args[i] == "--temp":
            if currblock.block["TEMPERATURE"] is None:
                currblock.set_param("TEMPERATURE",args[i+1])
        if args[i] == "--ph":
            currblock.set_param("$PH",args[i+1])
        if args[i] == "--mp":
            currblock.set_param("MP",args[i+1])
        if args[i] == "--bp":
            currblock.set_param("BP",args[i+1])
        if args[i] == "--ref":
            currblock.set_param("SOURCE REFERENCE",args[i+1])

        if args[i] == "--origin":
            currblock.set_param("ORIGIN",args[i+1])
        if args[i] == "--owner":
            currblock.set_param("OWNER",args[i+1])

        if args[i] == "--comment":
            currblock.set_param("$COMMENTS",args[i+1])


        #set date/time
        currblock.set_param("DATE",currdate)
        currblock.set_param("TIME",currtime)
        currblock.set_param("LONG DATE",currlongdate)

    #try to set reference value
    for block in jcamp.blocks:
        blockdic = block.block
        if ("JCAMP-DX" in blockdic) and (blockdic["DATA TYPE"] in ("NMR SPECTRUM","nD NMR SPECTRUM")):
            reflist = block._refvalues

            if ("C" in blockdic[".OBSERVE NUCLEUS"]) or ("H" in blockdic[".OBSERVE NUCLEUS"]):
                testcpd = reflist[1].upper()
                if ("TMS" in testcpd) or ("DSS" in testcpd) or ("TSP" in testcpd) or ("SIL" in testcpd):
                    if reflist[3] is None:
                        reflist[3] = 0.0

            if reflist[3] is not None:
                ppm = reflist[3]

                if ("NTUPLES" in blockdic) and (blockdic["NUM_DIM"] == "2"):

                    first = float(blockdic["FIRST"].split(',')[1])
                    last  = float(blockdic["LAST"].split(',')[1])
                    npoints = int(blockdic["VAR_DIM"].split(',')[1])

                else:

                    first = float(blockdic["FIRSTX"])
                    last  = float(blockdic["LASTX"])
                    npoints = int(blockdic["NPOINTS"])

                reflist[2] = "%.2f"%(interp1d(np.linspace(first, last, npoints), np.arange(npoints), fill_value="extrapolate")(ppm))

            blockdic[".SHIFT REFERENCE"] = ",".join(map(str, reflist))

            if blockdic["DATA TYPE"] == "nD NMR SPECTRUM":

                #print("HERE", blockdic["DATA TYPE"], file=sys.stderr)

                reflist_direct = block._refvalues
                reflist_indirect = ["INTERNAL","UNKNOWN",0,0]

                if ("C" in blockdic[".OBSERVE NUCLEUS"] or "H" in blockdic[".OBSERVE NUCLEUS"]):
                    reflist_indirect[1] = reflist_direct[1].upper()

                first = float(blockdic["FIRST"].split(',')[0])

                reflist_indirect[2] = 1
                reflist_indirect[3] = first
                blockdic["$INDIRECT REFERENCE"] = ",".join(map(str,reflist_indirect))


    jcamp.write()
    #sys.exit(0)

