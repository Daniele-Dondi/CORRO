import numpy as np

SQZ = { "0":"@", "1":"A", "2":"B", "3":"C", "4":"D", "5":"E",
                 "6":"F", "7":"G", "8":"H", "9":"I",
       "-0":"@","-1":"a","-2":"b","-3":"c","-4":"d","-5":"e",
                "-6":"f","-7":"g","-8":"h","-9":"i",}

DIF = { "0":"%", "1":"J", "2":"K", "3":"L", "4":"M", "5":"N",
                 "6":"O", "7":"P", "8":"Q", "9":"R",
       "-0":"%","-1":"j","-2":"k","-3":"l","-4":"m","-5":"n",
                "-6":"o","-7":"p","-8":"q","-9":"r",}

DUP = { "1":"S", "2":"T", "3":"U", "4":"V", "5":"W",
        "6":"X", "7":"Y", "8":"Z", "9":"s",}

def pseudo(string, dic):
    """
    convert a string representing a number to ASDF format given dic SQZ/DIF/DUP
    the first 1 or 2 chars are converted to a letter
    """
    string = string.strip()
    if string[0] == "-":
        return dic[string[:2]] + string[2:]
    else:
        return dic[string[:1]] + string[1:]

def to_pac(string):
    """
    convert a string representing a number to PAC format
    """
    string = string.strip()
    test = float(string)
    if test < 0:
        return string
    else:
        return " " + string


def xy_to_xydata(x, y, form="DIF", xfmt="%-10.4f", yfmt="%10.6g", width=80):

    """
    converts pairs of numbers (xi, yi) in separate arrays to xydata format
    returns a single string with newlines, and without the first format line
    form: AFFN, PAC, SQZ, DIF, SQZDUP, DIFDUP
    xfmt, yfmt: format for ASDF/AFFN and padding for AFFN format
    width: max line length
    """

    if len(x) != len(y): raise ValueError('x and y array size not equal')

    if form not in ('AFFN', 'PAC', 'SQZ', 'DIF', 'SQZDUP', 'DIFDUP'):
        raise ValueError('unknown xydata format: %s'%form)


    xstr = list(map(lambda v: xfmt%(v), x))
    ystr = list(map(lambda v: yfmt%(v), y))
    ydiff = [0]+[y[i]-y[i-1] for i in range(1,len(y))]
    dstr = list(map(lambda v: yfmt%(v), ydiff))

    if form != "AFFN":
        xstr = [v.strip() for v in xstr]

    if "PAC" in form:
        ystr = [to_pac(v) for v in ystr]
    elif ("SQZ" in form) or ("DIF" in form):
        ystr = [pseudo(v, SQZ) for v in ystr]

    if "DIF" in form:
        dstr = [pseudo(v, DIF) for v in dstr]

    block = []
    
    line = []
    size = 0
    i = 0
    while i <= len(xstr):

        #end of array
        if i >= len(xstr):
            block.append("".join(line))
            line = []
            #final checkpoint
            if "DIF" in form:
                line.append(xstr[-1])
                line.append(ystr[-1])
                block.append("".join(line))
            break

        #first x and y always present
        if len(line) == 0:

            line.append(xstr[i])
            line.append(ystr[i])
            size += len(xstr[i])
            size += len(ystr[i])
            i += 1

            if size >= width:
                block.append("".join(line))
                line = []
                size = 0
                continue

            #count if DUP
            if "DUP" in form:
                count = 1
                i -= 1
                for s in ystr[i+1:]:
                    if s == ystr[i]:
                        countstr = pseudo(str(count+1), DUP)
                        if size + len(countstr) <= width:
                            count += 1
                        else:
                            break
                    else:
                        break
                if count > 1:
                    countstr = pseudo(str(count), DUP)
                    line.append(countstr)
                    size += len(countstr)
                i += count

            if size >= width:
                block.append("".join(line))
                line = []
                size = 0
                continue
            
            continue

        #remaining values
        if "DIF" in form:
            arr = dstr
        else:
            arr = ystr

        line.append(arr[i])
        size += len(arr[i])
        i += 1


        if size >= width:

            #remove entry
            val = line.pop()
            size -= len(val)
            i -= 1

            block.append("".join(line))
            line = []
            size = 0
            #rewind if DIF
            if "DIF" in form:
                i -= 1
            continue

        #count if DUP
        if "DUP" in form:
            count = 1
            i -= 1
            for s in arr[i+1:]:
                if s == arr[i]:
                    countstr = pseudo(str(count+1), DUP)
                    if size + len(countstr) <= width:
                        count += 1
                    else:
                        break
                else:
                    break
            if count > 1:
                countstr = pseudo(str(count), DUP)
                line.append(countstr)
                size += len(countstr)
            i += count

        if size >= width:

            #remove entry
            val = line.pop()
            size -= len(val)
            i -= 1

            block.append("".join(line))
            line = []
            size = 0
            #rewind if DIF
            if "DIF" in form:
                i -= 1
            continue
        
        continue

    return "\n".join(block)


def xy_to_xypoints(x, y, xfmt="%10.4f", yfmt="%10.6g", width=80):

    """
    convert pairs of numbers (xi, yi) to xypoints format
    returns a string with newlines, without the first format line
    xfmt, yfmt: format for ASDF/AFFN and padding for AFFN format
    width: max line length
    """

    if len(x) != len(y): raise ValueError('x and y array size not equal')

    xstr = list(map(lambda v: xfmt%(v), x))
    ystr = list(map(lambda v: yfmt%(v), y))

    block = []
    
    line = []
    size = 0
    i = 0
    while i <= len(xstr):

        #end of array
        if i >= len(xstr):
            block.append(" ".join(line))
            line = []
            break

        #first x and y always present
        if len(line) == 0:

            tup = "%s, %s"%(xstr[i], ystr[i])
            line.append(tup)
            size += len(tup) + 1 #space
            i += 1

            if size >= width:
                block.append(" ".join(line))
                line = []
                size = 0
                continue
            
            continue

        #add more until filled

        if len(line) > 0:

            tup = "%s, %s"%(xstr[i], ystr[i])
            line.append(tup)
            size += len(tup) + 1 #space
            i += 1

            if size >= width:
                line.pop()
                block.append(" ".join(line))
                line = []
                size = 0
                i -= 1
                continue
            
            continue


    return "\n".join(block)



