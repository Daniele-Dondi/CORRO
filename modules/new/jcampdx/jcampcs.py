#import rdkit.Chem as Chem
#from rdkit.Geometry.rdGeometry import Point3D
import numpy as np

#already stripped currently
def strip_comments(line):
    if "$$" in line:
        line, _ = line.split("$$", 1)
    return line.strip()

def mol_to_molform(mol):

    """
    generates JCAMP style formula string from RDKit mol file
    """

    mol = Chem.AddHs(mol)

    frags = []

    for f in Chem.GetMolFrags(mol, asMols=True):

        atoms = {}

        for a in f.GetAtoms():

            sym = a.GetSymbol()
            iso = a.GetIsotope()

            if iso:
                s = "^%i%s"%(iso,sym)
            else:
                s = sym

            if s in atoms:
                atoms[s] += 1
            else:
                atoms[s] = 1

        frags.append(atoms)

    result = []

    for frag in frags:

        frag_form_CH = []
        frag_form_other = []

        c = [k for k in frag if k.endswith("C")]
        h = [k for k in frag if k.endswith("H")]

        for a in c:
            count = frag[a]
            if count > 1:
                frag_form_CH.append("%s%i"%(a,count))
            else:
                frag_form_CH.append("%s"%(a))
 
        for a in h:
            count = frag[a]
            if count > 1:
                frag_form_CH.append("%s%i"%(a,count))
            else:
                frag_form_CH.append("%s"%(a))

        for a in frag:
            if a in c: continue
            if a in h: continue
            count = frag[a]
            if count > 1:
                frag_form_other.append("%s%i"%(a,count))
            else:
                frag_form_other.append("%s"%(a))

        frag_form_other.sort(key=lambda s: "".join(c for c in s if c.isalpha()))

        result.append(" ".join(frag_form_CH + frag_form_other))

    return " * ".join(result)

def mol_to_cs(mol):

    """
    converts rdkit mol file to dictionary of jcamp-cs LDRs
    """

    block = {}

    atomblock = []
    chargeblock = {}
    stereoblock = []
    radblock = {}
    bondblock = []
    stereobonds = []

    for a in mol.GetAtoms():

        sym = a.GetSymbol()
        idx = str(a.GetIdx()+1)
        val = a.GetImplicitValence()
        chg = a.GetFormalCharge()
        rad = a.GetNumRadicalElectrons()
        chi = a.GetChiralTag()
        #TODO: add isotope to atom sym

        atomblock.append("%s %s %s"%(idx, sym, val))

        if chg:
            if chg > 0:
                chg = "+" + str(chg)
            elif chg < 0:
                chg = str(chg)
            if chg not in chargeblock:
                chargeblock[chg] = []
            chargeblock[chg].append(idx)

        if chi == Chem.ChiralType.CHI_TETRAHEDRAL_CCW:
            stereoblock.append("%s %s 0"%(idx, "M"))
        if chi == Chem.ChiralType.CHI_TETRAHEDRAL_CW:
            stereoblock.append("%s %s 0"%(idx, "P"))

        if rad:
            if a not in radblock:
                radblock[a] = []
            radblock[a].append(idx)

    bondtypedic = {1:"S",2:"D",3:"T",4:"Q"}
    nonstereo = (Chem.BondStereo.STEREOANY, Chem.BondStereo.STEREONONE)
    stereo_m = (Chem.BondStereo.STEREOTRANS, Chem.BondStereo.STEREOE)
    stereo_p = (Chem.BondStereo.STEREOCIS, Chem.BondStereo.STEREOZ)

    for b in mol.GetBonds():

        begin = b.GetBeginAtomIdx()+1
        end = b.GetEndAtomIdx()+1
        bondtype = b.GetBondTypeAsDouble()
        stereo = b.GetStereo()

        if bondtype in bondtypedic:
            bondtype = bondtypedic[bondtype]
        else:
            bondtype = "A"
        bondblock.append("%s %s %s"%(begin, end, bondtype))


        if stereo not in nonstereo:
            if stereo in stereo_m:
                stereo = "M"
            if stereo in stereo_p:
                stereo = "P"

            stereoatoms = [a+1 for a in b.GetStereoAtoms()]
            bondatoms = begin, end
            stereoligands = [[n.GetIdx()+1 for n in mol.GetAtomWithIdx(a-1).GetNeighbors()] for a in bondatoms]
            flipstereo = 0
            if stereoatoms[0] != min(stereoligands[0]): flipstereo += 1
            if stereoatoms[1] != min(stereoligands[1]): flipstereo += 1
            if flipstereo%2:
                if stereo == "M": stereo == "P"
                if stereo == "P": stereo == "M"

            stereobonds.append("%s %s %s 0"%(bondatoms[0], bondatoms[1], stereo))

    block['MOLFORM'] = [mol_to_molform(mol)]
    block['ATOMLIST'] = [""] + atomblock
    block['BONDLIST'] = [""] + bondblock
    if chargeblock:
        block['CHARGE'] = [""] + [c + " " + " ".join(chargeblock[c]) for c in chargeblock]
    if radblock:
        block['RADICAL'] = [""] + [str(n) + " " + " ".join(radblock[n]) for n in radblock]
    if stereoblock:
        block['STEREOCENTER'] = [""] + stereoblock
    if stereobonds:
        block['STEREOPAIR'] = [""] + stereobonds

    try:
        conformer = mol.GetConformer()
    except:
        for k in block:
            block[k] = "\n".join(block[k])
        return block

    coordblock = []

    if conformer.Is3D():
        #XYZ
        coords = conformer.GetPositions()
        block['MAX_XYZ'] = [str(np.max(np.abs(coords)))]
        block["XYZ_FACTOR"] = ["0.01"]
        coords *= 100
        coords = coords.astype(int)
        for i in range(len(coords)):
            idx = str(i+1)
            xyz = " ".join(map(str, coords[i]))
            coordblock.append(idx + " " + xyz)
        block['XYZ'] = [""] + coordblock

    else:
        coords = conformer.GetPositions()
        block['MAX_RASTER'] = [str(np.max(np.abs(coords)))]
        block["XY_RASTER_FACTOR"] = ["0.01"]
        coords *= 100
        coords = coords.astype(int)
        for i in range(len(coords)):
            idx = str(i+1)
            xyz = " ".join(map(str, coords[i]))
            coordstr = idx + " " + xyz
            atom = mol.GetAtomWithIdx(i)
            bonds = atom.GetBonds()
            bonddir = ""
            for b in bonds:
                if b.GetBeginAtomIdx() == i:
                    if b.GetBondDir() == Chem.BondDir.BEGINDASH:
                        coordstr += " -1"
                    if b.GetBondDir() == Chem.BondDir.BEGINWEDGE:
                        coordstr += " +1"
            coordblock.append(coordstr)
        block['XY_RASTER'] = [""] + coordblock

    for k in block:
        block[k] = "\n".join(block[k])

    return block


def cs_to_mol(block):

    """
    converts dictionary of jcamp-cs LDRs to an rdkit mol
    some unconvrtable data, eg stereogroups are ignored
    """

    if "JCAMP-CS" not in block:
        raise ValueError('Not a JCAMP-CS block')

    if float(block["JCAMP-CS"][0]) > 3.7:
        raise ValueError('Unsupported JCAMP-CS version')

    if "$MOLFILE" in block:
        return Chem.MolFromMolBlock("\n".join(block["$MOLFILE"]), removeHs=False)

    mol = Chem.RWMol()

    atom_old_new_idx = {}
    atom_new_old_idx = {}

    print("DEBUG", block["ATOMLIST"])
    sorted_atoms = [strip_comments(line).split() for line in block["ATOMLIST"] if strip_comments(line)]
    sorted_atoms.sort(key=lambda x: int(x[0]))

    for line in sorted_atoms:
        old_idx, sym, imp_H = line
        new_idx = mol.AddAtom(Chem.Atom(sym))
        if old_idx in atom_old_new_idx:
            raise ValueError('atom with same index exists')
        atom_old_new_idx[old_idx] = new_idx
        atom_new_old_idx[new_idx] = old_idx
        mol.GetAtomWithIdx(new_idx).SetNumExplicitHs(int(imp_H))

    bondtype = {"S":Chem.BondType.SINGLE, 
                "D":Chem.BondType.DOUBLE,  
                "T":Chem.BondType.TRIPLE, 
                "Q":Chem.BondType.QUADRUPLE, 
                "A":Chem.BondType.OTHER, }

    for line in block["BONDLIST"]:
        line = strip_comments(line).split()
        if not line: continue
        id1, id2, order = line
        newid1, newid2 = atom_old_new_idx[id1], atom_old_new_idx[id2]
        mol.AddBond(newid1, newid2, bondtype[order])

    if "CHARGE" in block:
        for line in block["CHARGE"]:
            line = strip_comments(line).split()
            if not line: continue
            charge = int(line[0])
            for old_idx in line[1:]:
                new_idx = atom_old_new_idx[old_idx]
                mol.GetAtomWithIdx(new_idx).SetFormalCharge(charge)

    if "RADICAL" in block:
        for line in block["RADICAL"]:
            line = strip_comments(line).split()
            if not line: continue
            nelec = int(line[0])
            for old_idx in line[1:]:
                new_idx = atom_old_new_idx[old_idx]
                mol.GetAtomWithIdx(new_idx).SetNumRadicalElectrons(nelec)

    stereo_m = (Chem.BondStereo.STEREOTRANS, Chem.BondStereo.STEREOE)
    stereo_p = (Chem.BondStereo.STEREOCIS, Chem.BondStereo.STEREOZ)

    if "STEREOCENTER" in block:
        for line in block["STEREOCENTER"]:
            line = strip_comments(line).split()
            if not line: continue
            old_idx, stereo, group = line
            new_idx = atom_old_new_idx[old_idx]
            if group != "0": continue
            atom = mol.GetAtomWithIdx(new_idx)
            if stereo == "M":
                atom.SetChiralTag(Chem.ChiralType.CHI_TETRAHEDRAL_CCW)
            if stereo == "P":
                atom.SetChiralTag(Chem.ChiralType.CHI_TETRAHEDRAL_CW)

    if "STEREOPAIR" in block:
        for line in block["STEREOCENTER"]:
            line = strip_comments(line).split()
            if not line: continue
            idx1, idx2, stereo, group = line
            newid1, newid2 = atom_old_new_idx[idx1], atom_old_new_idx[idx2]
            bond = mol.GetBondBetweenAtoms(newid1, newid2)
            if group != "0": continue
            #cis is P, trans is M, for lowest atom idxs on each side of bond
            #using original numbering
            begin_neighs = mol.GetAtomWithIdx(newid1).GetNeighbors()
            end_neighs = mol.GetAtomWithIdx(newid2).GetNeighbors()

            begin_neigh_ids = [n.GetIdx() for n in begin_neighs if n.GetIdx() != newid2]
            end_neigh_ids = [n.GetIdx() for n in begin_neighs if n.GetIdx() != newid1]

            old_begin_id = min([int(atom_new_old_idx[i]) for i in begin_neigh_ids])
            old_end_id = min([int(atom_new_old_idx[i]) for i in end_neigh_ids])

            new_begin_id = atom_old_new_idx[old_begin_id]
            new_end_id = atom_old_new_idx[old_end_id]

            dih = Chem.rdMolTransforms.GetDihedralDeg(mol.GetConformer, new_begin_id, newid1, newid2, new_end_id)
            if -90 <= dih < 90:
                bond.SetStereo(Chem.BondStereo.STEREOCIS)
                bond.SetStereoAtoms(new_begin_id, new_end_id)
            else:
                bond.SetStereo(Chem.BondStereo.STEREOTRANS)
                bond.SetStereoAtoms(new_begin_id, new_end_id)

    #TODO: set 3D flag appropriately
    if "XYZ" in block: 
        if "XYZ_FACTOR" in block:
            factor = float(block["XYZ_FACTOR"][0])
        else:
            factor = 1
        coords = np.zeros((mol.GetNumAtoms(), 3))
        conf = Chem.Conformer(mol.GetNumAtoms())
        for line in block["XYZ"]:
            line = strip_comments(line).split()
            if not line: continue
            oldidx, x, y, z = line[:3]
            coords[atom_old_new_idx[oldidx]][0] = float(x)*factor
            coords[atom_old_new_idx[oldidx]][1] = float(y)*factor
            coords[atom_old_new_idx[oldidx]][2] = float(z)*factor
        for i in range(len(coords)):
            pos = Point3D(coords[i][0], coords[i][1], coords[i][2])
            conf.SetAtomPosition(i, pos)
        mol.AddConformer(conf)

    elif "XY_RASTER" in block: 
        if "XY_RASTER_FACTOR" in block:
            factor = float(block["XY_RASTER_FACTOR"][0])
        else:
            factor = 1
        coords = np.zeros((mol.GetNumAtoms(), 3))
        conf = Chem.Conformer(mol.GetNumAtoms())
        print("DEBUG", coords)
        print("DEBUG", block["XY_RASTER"])
        for line in block["XY_RASTER"]:
            line = strip_comments(line).split()
            if not line: continue
            oldidx, x, y = line[:3]
            coords[atom_old_new_idx[oldidx]][0] = float(x)*factor
            coords[atom_old_new_idx[oldidx]][1] = float(y)*factor
            #TODO: 
            #ignore wedges?, use chirality only
            #wedge all bonds to this atom?
            if len(line) == 4:
                coords[atom_old_new_idx[oldidx]][2] = float(line[3])*factor
        for i in range(len(coords)):
            pos = Point3D(coords[i][0], coords[i][1], coords[i][2])
            conf.SetAtomPosition(i, pos)
        mol.AddConformer(conf)

        
    mol = mol.GetMol()
    mol.UpdatePropertyCache()

    return mol
    




