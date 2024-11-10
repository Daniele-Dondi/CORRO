import os, sys
import zlib
import glob

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
    directory = '*.py'  # Example to match text files
    for filename in glob.glob(directory):
        CRCValues.append(CRC(filename))
    directory = 'modules/*.py'  # Example to match text files
    for filename in glob.glob(directory):
        CRCValues.append(CRC(filename))
    with open("CRCValues",mode="w") as file:
         file.writelines(CRCValues)
    GlobalCRC=CRC("CRCValues")
    with open("CRCValues",mode="w") as file:
        file.write(GlobalCRC)
    return not (GlobalCRC==OldGlobalCRC)

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



