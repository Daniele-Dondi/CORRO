import os, sys
import zlib

def CRC(fileName):
    CRC32 = 0
    for content in open(fileName,"rb"):
        CRC32 = zlib.crc32(content, CRC32)
    return "%X"%(CRC32 & 0xFFFFFFFF)

print(CRC("builtvercalculator.py"))
