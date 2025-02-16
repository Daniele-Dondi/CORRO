# Copyright (C) 2025 Daniele Dondi
#
# This work is licensed under a Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/
#
# You are free to:
# - Share: copy and redistribute the material in any medium or format
# - Adapt: remix, transform, and build upon the material for any purpose, even commercially
#
# Under the following terms:
# - Attribution: You must give appropriate credit, provide a link to the license, and indicate if changes were made.
#   You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
# - No additional restrictions: You may not apply legal terms or technological measures that legally restrict
#   others from doing anything the license permits.
#
# Author: Daniele Dondi
# Date: 2025

import os, sys
import zlib
import glob
from datetime import datetime

def CRC(fileName):
    CRC32 = 0
    for content in open(fileName,"rb"):
        CRC32 = zlib.crc32(content, CRC32)
    return "%X"%(CRC32 & 0xFFFFFFFF)

def FilesHasBeenModified():
    OldGlobalCRC=""
    try:
        with open("CRCValues",mode="r") as file:
            OldGlobalCRC=file.readline()
    except:
        pass
    CRCValues=[]
    TotalLines=0
    directory = '*.py'  # Example to match text files
    for filename in glob.glob(directory):
        with open(filename,'r') as textfile: TotalLines+=len(textfile.readlines())
        CRCValues.append(CRC(filename))
    directory = 'modules/*.py'  # Example to match text files
    for filename in glob.glob(directory):
        with open(filename,'r') as textfile: TotalLines+=len(textfile.readlines())
        CRCValues.append(CRC(filename))
    with open("CRCValues",mode="w") as file:
         file.writelines(CRCValues)
    GlobalCRC=CRC("CRCValues")
    with open("CRCValues",mode="w") as file:
        file.write(GlobalCRC)
    Changed=not (GlobalCRC==OldGlobalCRC)
    if Changed:
        try:
            with open("stats.txt",'a') as outfile: outfile.write(str(datetime.now())+" total lines: "+str(TotalLines)+"\n")
        except:
            pass
    return Changed

def GetBuildVersion():
    try:
     BuildVerFile=open("build","r")
     BuildVersion=int(BuildVerFile.readline())
     BuildVerFile.close()
     if BuildVersion<0: BuildVersion=0
    except:
     BuildVersion=0
    if FilesHasBeenModified():
        BuildVersion+=1
        try:
         BuildVerFile=open("build","w")
         BuildVerFile.write(str(BuildVersion))
         BuildVerFile.close()
        except:
         pass
    return BuildVersion



