import numpy as np
import os

import tkinter as tk
from tkinter import filedialog

HEADER_BLOCK="""
##TITLE=UniPavia_1D_1H_20251016_Xylenolligand
##JCAMP-DX=5.01 $$ Nanalysis NMReady v3.1.0.8, 2024.12.1, 21.2.0, 218.1.0, 2024.11.29
##DATA TYPE=NMR FID
##DATA CLASS=NTUPLES
##ORIGIN=Nanalysis Corp.
##OWNER=Nanalysis
##LONG DATE=2025/10/16 09:56:09+0200
##SPECTROMETER/DATA SYSTEM=NMReady 100/nanalysis-lx011
##INSTRUMENTAL PARAMETERS=^1H
##TEMPERATURE=32.00000123795625
##PRESSURE=1.000000  $$ Bar
##RESOLUTION=0.00081010328140
##SAMPLE DESCRIPTION=
##.OBSERVE FREQUENCY=61.72052520739037
##.OBSERVE NUCLEUS=^1H
##.SOLVENT NAME=D2O
##.ACQUISITION MODE=SIMULTANEOUS
##.SHIFT REFERENCE=INTERNAL, D2O, 4096, 7.00000000000000
##.SOLVENT REFERENCE=7.00000000000000
##.DELAY=(0.000000,0.000000)
##.FIELD=0.000000  $$ Tesla
##.OBSERVE 90=10.730000
##.ACQUISITION TIME=6.63636608119716
##.ZERO FILL=0
##.AVERAGES=16
##.DIGITISER RES=16
##.SPINNING RATE=0.000000
$$##.PHASE 0=7.05767804437147
$$##.PHASE 1=-98.45101178240641
$$ NMReady specific parameters
##$COMMENT=
##$SCANS=16
##$SCAN DELAY=1.000000
##$TOTAL DURATION=146.276995
##$ACQUISITION START TIME=1760601187.8218877
##$90 PULSE=10.730000, 22.440000
##$180 PULSE=21.460000, 44.880000
##$RECVR_GAIN=45.0
##$SPECTRAL WIDTH=20.000000
##$RELAXATIONDELAY=7.636438
##$ZEROING=7.000000
##$APODIZATION=0.100000
##$PHASECORRECTION=7.057678,-98.451012
##$PIVOT=0.000000
##$AUTOMATICBASELINECORRECTION=0
##$MANUALBASELINEOFFSET=0.000000
##$BASELINEMETHOD=2
##$BASELINEMETHODSTRING=SNIP
##$BASELINELEGACYSIGMAFACTOR=3.0
##$BASELINELEGACYREGIONSIZEPPM=0.2
##$BASELINELEGACYSMOOTHINGFACTOR=10000.0
##$BASELINEMAXHALFWINDOW=64
##$BASELINESMOOTHHALFWINDOW=0
##$BASELINELAM=1000000.0
##$BASELINEETA=0.5
##$DT=0.000810
##$LOCKOFFSET=4.790000
##$SPECTRALCENTER=7.000000
##$DECIMATION=1
##$LOWESTF2=-185.161576
##$T2NUCLEUS=1H
##$PULSE_AMPLITUDE=71.000000
##$EXPERIMENT=1D
##$PLOTTYPE=1D
##$GYRO=42575500.000000
##$INTEGRALS_MANUAL_REFERENCE INTEGRAL=1.0
##$INTEGRALSTHRESHOLDMULTIPLIER=0.5
##$PEAKSTHRESHOLDMULTIPLIER=0.5
##$DECOUPLINGSETTINGS_MODE=Off
##$RDC_ENABLED=1
##$RDC_TYPE=FivePar
##$RDC_PARAMETERS=(1,7.5198746987355020721111032,0.98292109582189879368741003,
0.77399254946772844121483104,0.91444980072334547394063975)
##$APPLICATIONPARAMETER_RECEIVER_GAIN=0.0
##$APPLICATIONPARAMETER_RECEIVER_GAIN_FIXED_OR_AUTO=Auto
##$APPLICATIONPARAMETER_PULSE_ANGLE_DEGREES=90.0
##$EXPERIMENT_SETTING_SPECTRAL_WIDTH=20
##$EXPERIMENT_SETTING_SPECTRAL_CENTER=7.0
##$EXPERIMENT_SETTING_NUMBER_OF_POINTS=8192
##$EXPERIMENT_SETTING_SCAN_DELAY=1.0
##$EXPERIMENT_SETTING_NUMBER_OF_SCANS=16
##$EXPERIMENT_SETTING_DUMMY_SCANS=0
##$EXPERIMENT_SETTING_RECEIVER_GAIN=45.00, Auto
##$EXPERIMENT_SETTING_PULSE_ANGLE_(°)=90.0
##$EXPERIMENT_SETTING_FILENAME=UniPavia_1D_1H_20251016_Xylenolligand.dx
##$SIGNAL1_AMPLITUDE=71.0,71.0
##$SIGNAL1_ATTENUATION=7,7
##$SIGNAL1_POWER=1.005,1.005
##$SIGNAL1_CPD_POWER=0.01922,0.01922
##$SIGNAL2_AMPLITUDE=71.0,71.0
##$SIGNAL2_ATTENUATION=3,3
##$SIGNAL2_POWER=5.049,5.049
##$SIGNAL2_CPD_POWER=0.2601,0.2601
##$BASELINE_FIX=0
$$ End of NMReady specific parameters
$$ Bruker specific parameters
$$ --------------------------
##$DATE=1760601334
##$SI= 65536
##$TDeff= 0
##$SFO1= 61.72052520739037
##$O1= 432.04367645173261
##$SF= 61.72009316371392
##$BF1= 61.72009316371392
##$AQ= 6.63636608119716
##$SWH= 1234.41050414780784
##$SW= 20.00000000000001
##$SR= 0.00000000000000
##$OFFSET= 17.00011900093960
##$FIDRES= 0.15068487599461
##$O1P= 7.00000000000000
##$TD= 16384
##$DW= 405.05164069806892
##$SPECTYP= PROTON
##$NS= 16
##$DS= 0
##$DR= 16
##$DE=10.000000
##$RG=45
##$P1=10.730000
##$P= (0..2)
0.0 10.730000
##$DECIM=2
##$DIGTYP=17
##$DSPFVS=21
##$GRPDLY=34.0
##$PHC0=-56.28318393557468
##$PHC1=98.45101178240641
##$PH_mod=1
##$WDW= 1
##$LB= 0.10000000000000
##$GB= 0.00000000000000
##$SSB= 0.00000000000000
##$TM1= 0.00000000000000
##$TM2= 0.00000000000000
$$ End of Bruker specific parameters
$$ ---------------------------------
##NPOINTS=8192
##DELTAX=0.0008101033
##NTUPLES=NMR FID
##VAR_NAME=TIME,FID/REAL,FID/IMAG,PAGE NUMBER
##SYMBOL=X,R,I,N
##VAR_TYPE=INDEPENDENT,DEPENDENT,DEPENDENT,PAGE
##VAR_FORM=AFFN,AFFN,AFFN,AFFN
##VAR_DIM=8192,8192,8192,2
##UNITS=SECONDS,ARBITRARY UNITS,ARBITRARY UNITS,
##FIRST=0.000000,0.000000,0.000000,1
##LAST=6.636366,24.215750,-40.459495,2
##MIN=0.000000,-137057.824070,-105754.483637,1
##MAX=6.636366,173125.949697,125061.091648,2
##FACTOR=0.00081010328139613790,0.00008061807692858350,0.00008061807692858350,1
##PAGE=N=1
##DATA TABLE= (X++(R..R)), XYDATA
"""

END_BLOCK="""
##PAGE=N=2
##DATA TABLE= (X++(I..I)), XYDATA
"""

END_FILE="""
##END NTUPLES=NMR FID
##END=
"""

def replace_first_column(arrays, step=16.0):
    updated = []
    for arr in arrays:
        new_x = np.arange(len(arr)) * step
        arr_copy = arr.copy()
        arr_copy[:, 0] = new_x
        updated.append(arr_copy)
    return updated

def parse_block(block_lines):
    data = []
    for line in block_lines:
        if line.strip() and not line.startswith('##'):
            parts = line.strip().split()
            row = [float(p) for p in parts]
            data.append(row)
    return np.array(data)

def extract_blocks(filename):
    R, I = [], []
    with open(filename, 'r') as f:
        lines = f.readlines()

    current_block = []
    current_type = None
    in_block = False

    for line in lines:
        if '##DATATABLE= (T2++(R..R)), PROFILE' in line:
            in_block = True
            current_type = 'R'
            current_block = []
        elif '##DATATABLE= (T2++(I..I)), PROFILE' in line:
            in_block = True
            current_type = 'I'
            current_block = []
        elif '##PAGE' in line and in_block:
            in_block = False
            data_array = parse_block(current_block)
            if current_type == 'R':
                R.append(data_array)
            elif current_type == 'I':
                I.append(data_array)
        elif in_block:
            current_block.append(line)

    return R, I

# Example usage:
# R_blocks, I_blocks = extract_blocks('your_file.txt')

def load_FID():
    file_path = filedialog.askopenfilename(
        title="Select JCAMP File",
        filetypes=[("JCAMP-DX files", "*kinetic*.dx")]
    )
    
    if file_path:
        R_blocks, I_blocks = extract_blocks(file_path)
        R_updated = replace_first_column(R_blocks, step=16.0)
        I_updated = replace_first_column(I_blocks, step=16.0)

        output_dir = os.path.splitext(file_path)[0]
        base_filename = os.path.basename(file_path) 
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Write each pair of R and I arrays to a file
        for idx, (r_array, i_array) in enumerate(zip(R_updated, I_updated)):
            filename = os.path.join(output_dir, f"{base_filename}_block_{idx+1}.dx")
            with open(filename, 'w') as f:
                # Write header
                f.write(HEADER_BLOCK)

                # Write R block
                for row in r_array:
                    f.write("  ".join(f"{val:12.8f}" for val in row) + "\n")

                # Write END_BLOCK
                f.write(END_BLOCK)

                # Write I block
                for row in i_array:
                    f.write("  ".join(f"{val:12.8f}" for val in row) + "\n")

                # Final END_FILE
                f.write(END_FILE)
        print(len(R_updated),"files written.")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("JCAMP KINETIC EXTRACTOR")
    root.geometry("300x150")

    load_button = tk.Button(root, text="Load JCAMP File", command=load_FID)
    load_button.pack(pady=50)

    # Run the GUI loop
    root.mainloop()
