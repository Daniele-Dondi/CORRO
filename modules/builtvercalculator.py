import os, sys
import zlib

def crc(fileName):
    CRC32 = 0
    for eachLine in open(fileName,"rb"):
        CRC32 = zlib.crc32(eachLine, CRC32)
    return "%X"%(CRC32 & 0xFFFFFFFF)
