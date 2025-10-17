"""
functions for parsing jcamp files
"""

def split_jcamp(f):


    """
    reads jcamp file and returns nested lists of lines
    """

    blocks = []
    levels = [blocks]

    for line in f:

        if line.startswith("##TITLE="):
            #start new block
            curr_block = []
            levels.append(curr_block)
            levels[-1].append(line)

        elif line.startswith("##END="):
            #finish block
            levels[-1].append(line)
            block = levels.pop()
            levels[-1].append(block)

        else:
            levels[-1].append(line)

    return blocks

def split_record(line):

    """
    splits labeled-data-record into label and data
    lines without labels (comment lines or multiline records) return label=None
    comments are striped
    """

    if "$$" in line:
        line, _ = line.split("$$", 1)

    if line.startswith("##"):
        label, line = line.split("=", 1)
        label = label.replace("##","").strip()
    else:
        label = None

    line = line.strip()

    return label, line



def jcamp_to_dic(linelist):

    """
    recursively parse nested lists from split_jcamp() to nested dicts
    for each block:
    each ldr is key=list (of strings)
    nested blocks are placed in a list of dicts under key=SUBBLOCKS
    pages from ntuples are placed in a list of dicts under key=PAGES
    """

    block = {}
    curr_label = None
    page_data = {}
    is_page = False
    brukerflag = ""

    for line in linelist:

        if type(line) is str:

            #comments stripped here
            label, data = split_record(line)

            #prepend F1, F2 etc for bruker data
            if line.startswith("$$ Bruker specific parameters"):
                tmp = line.split("for")
                if len(tmp) > 1:
                    brukerflag = tmp[1].strip()
            if line.startswith("$$ End of Bruker specific parameters"):
                brukerflag = ""

            if brukerflag and label:
                if label.startswith("$"):
                    label = "$%s_%s"%(brukerflag, label[1:])
                #print(label)

            #normalize some labels
            if label == "JCAMPDX":
                label = "JCAMP-DX"
            if label == "NUM_DIM":
                label = "NUM DIM"
            if label == "DATA TYPE" and data == "nD NMR SPECTRUM":
                data = "NMR SPECTRUM"
            if label == "DATA TYPE" and data == "nD NMR FID":
                data = "NMR FID"

        elif type(line) is list:
            label = "SUBBLOCKS"
            data = jcamp_to_dic(line)

        if label: 
            curr_label = label
        elif label == "": #ignore ##= comments
            curr_label = None

        if curr_label == "END": 
            is_ntuples = False

        #make section for ntuples
        if curr_label == "PAGE":
            is_page = True
            if "PAGES" not in block:
                block["PAGES"] = []

        #new page
        if is_page and ((curr_label == "PAGE") or (curr_label == "END NTUPLES")):
            if page_data:
                block["PAGES"].append(page_data)
                page_data = {}

        #add data
        if curr_label:

            #skip empty or comment lines
            if data == "":
                continue

            #create or append to key
            #2D or higher BRUKER spectra with repeating parameters from 
            #different dimensions will not write back out correctly
            #will appear like a multiline LDR in ..., F3, F2, F1 order
            if is_page and (curr_label in ("PAGE", "DATA TABLE", "FIRST", "NPOINTS")):

                if curr_label not in page_data:
                    page_data[curr_label] = [data]
                else:
                    page_data[curr_label].append(data)

            else:
                if curr_label not in block:
                    block[curr_label] = [data]
                else:
                    block[curr_label].append(data)

    return block


def parse_jcamp(filename):

    """
    main function
    """

    with open(filename) as f:
        data = jcamp_to_dic(split_jcamp(f))

    return data



