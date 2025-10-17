import numpy as np
import string

SQZ = {"@": "0",
       "A": "1", "B": "2", "C": "3", "D": "4", "E": "5",
       "F": "6", "G": "7", "H": "8", "I": "9",
       "a": "-1", "b": "-2", "c": "-3", "d": "-4", "e": "-5",
       "f": "-6", "g": "-7", "h": "-8", "i": "-9"}
DIF = {"%": "0",
       "J": "1", "K": "2", "L": "3", "M": "4", "N": "5",
       "O": "6", "P": "7", "Q": "8", "R": "9",
       "j": "-1", "k": "-2", "l": "-3", "m": "-4", "n": "-5",
       "o": "-6", "p": "-7", "q": "-8", "r": "-9"}
DUP = {"S": "1", "T": "2", "U": "3", "V": "4", "W": "5",
       "X": "6", "Y": "7", "Z": "8", "s": "9"}

def split_xydata(line):

    """
    splits a string of a single line of a ASDF or AFFN encoded data table
    for XYDATA, PROFILE, XYPOINTS, etc
    returns a list of strings
    """

    line = line.strip()

    data = []

    curr_val = []
    pos = 0
    while pos <= len(line):

        #end of line
        if pos >= len(line):
            if curr_val:
                data.append("".join(curr_val))
                curr_val = []
            pos += 1
            break

        c = line[pos]

        #first char
        if not curr_val:
            if not c.isspace():
                curr_val.append(c)
            pos += 1
            continue

        #following char inc decimal
        if c.isdigit() or c == ".":
            curr_val.append(c)
            pos += 1
            continue

        #exponent E+/-004
        if c in ("E","e"):
            if (pos+2) < len(line):
                if line[pos+1] in ("+","-"):
                    curr_val.append(line[pos:pos+2]) #E+/-
                    pos += 2
                    c = line[pos]
                    while c.isdigit(): #expoenent
                        curr_val.append(c)
                        pos += 1
                        if pos >= len(line): 
                            break
                        else: 
                            c = line[pos]
                    continue

        #finish and start new if non-digit in middle of line
        if not c.isdigit():
            if curr_val:
                data.append("".join(curr_val))
            curr_val = []
            if not c.isspace():
                curr_val.append(c)
            pos += 1
            continue


    return data
                            

def parse_xydata(values):

    """
    decodes a list of strings representing one line of XYDATA
    returns the x value (first value), the following y values (the first y value
    is paired with the first x value), and flag "checkpoint" if the last y value
    was DIF encoded. If "checkpoint" is True, the last y value of this line, and
    the first y value of the NEXT line should match.
    """

    #first value is always x
    x = float(values[0])

    data = [] #tuples of float, dif?
    pos = 1

    while pos < len(values):

        val = values[pos]

        try: #pac or affn?
            n = float(val)
            data.append((n, False))
        except:
            try: #sqz?
                if val == "?":
                    n = 'nan'
                else:
                    n = "".join(SQZ[c] if c in SQZ else c for c in val)
                data.append((float(n), False))
            except:
                try: #dif?
                    n = "".join(DIF[c] if c in DIF else c for c in val)
                    data.append((float(n), True))
                except:
                    try: #dup?
                        n = "".join(DUP[c] if c in DUP else c for c in val)
                        last = data.pop()
                        data.extend([last]*int(n))
                    except:
                        raise ValueError('invalid item in xydata')
        pos += 1

    #final decoded y values
    y = []
    #if DIF, check that last of current line = first of next line
    checkpoint = False 
    for val, dif in data:
        if dif:
            y.append(y[-1] + val)
            checkpoint = True
        else:
            y.append(val)
            checkpoint = False

    return x, y, checkpoint

def xydata_to_y(block):

    """
    parses a list the lines from a single DATA TABLE or XYDATA record
    the first line in the input that details the format (eg "(X++(Y..Y))") is 
    skipped.
    only the y values are returned
    x is calculated using FIRSTX, LASTX, and DELTA=(LASTX-FIRSTX)/(NPOINTS-1)
    """

    ally = []
    checkfirst = False

    for line in block[1:]:

        x, y, checktmp = parse_xydata(split_xydata(line))

        #if DIF, check that first of current line = last of prev line
        if checkfirst:

            if ally[-1] != y[0]:
                raise ValueError('checkpoint failed')
            else:
                ally.pop()

        ally.extend(y)

        checkfirst = checktmp

    return ally




def parse_tabular(lines, single_group=False):
    
    """
    parse JCAMP tabular data/lines, eg from PEAK TABLE or PEAK ASSIGNMENTS
    grouped data (round brackets) and quoted strings (using "<" and ">") are 
    supported
    input is a list of lines
    output is a list of list of strings
    """

    inquote = False
    inbracket = False
    aftercomma = False
    afterspace = False

    result = []
    group = []
    item = []

    for line in lines:
        for c in line:

            if (c == "(") and not inquote:
                #print(c, "START GROUP")
                inbracket = True
                aftercomma = False
                afterspace = False
                if item:
                    group.append("".join(item))
                    item = []
                if group:
                    result.append(group)
                    group = []
                continue

            if (c == ")") and not inquote and inbracket:
                #print(c, "END GROUP")
                inbracket = False
                aftercomma = False
                afterspace = False
                if item:
                    group.append("".join(item))
                    item = []
                if group:
                    result.append(group)
                    group = []
                continue

            if (c == ",") and not inquote:
                #print(c, "END ITEM")
                if afterspace and aftercomma:
                    group.append("".join(item))
                    item = []
                aftercomma = True
                afterspace = False
                if item:
                    group.append("".join(item))
                    item = []
                continue

            if (c == ";") and not inquote:
                #print(c, "END ITEM/GROUP")
                aftercomma = False
                afterspace = False
                if item:
                    group.append("".join(item))
                    item = []
                if group:
                    result.append(group)
                    group = []
                continue


            if (c in (" ", "\t", "\n")) and not inquote and not single_group:
                #print(c, "WHITESPACE")
                afterspace = True
                if item:
                    group.append("".join(item))
                    item = []
                continue



            if (c == "<") and not inquote:
                #print(c, "START QUOTE")
                inquote = True
                aftercomma = False
                afterspace = False
                if item:
                    group.append("".join(item))
                    item = []
                continue

            if (c == ">") and inquote:
                #print(c, "END QUOTE")
                inquote = False
                aftercomma = False
                afterspace = False
                if item:
                    group.append("".join(item))
                    item = []
                continue

            if inquote or (c not in (" ", "\t", "\n")):
                #print(c, aftercomma, afterspace)
                if afterspace and not aftercomma:
                    if group:
                        #print("AFTER SPACE", "END GROUP")
                        result.append(group)
                        group = []
                aftercomma = False
                afterspace = False
                item.append(c)

            if not inquote and single_group and (c in (" ", "\t", "\n")):
                #print(c, "WHITESPACE")
                if item:
                    item.append(c)



        #End of line
        if aftercomma:
            group.append("".join(item))
            item = []
        if item and not inquote:
            #print("EOL", "END ITEM")
            group.append("".join(item))
            item = []
        if group and not inbracket:
            #print("EOL", "END GROUP")
            result.append(group)
            group = []
        aftercomma = False
        afterspace = False

    #print(result)
    return result






