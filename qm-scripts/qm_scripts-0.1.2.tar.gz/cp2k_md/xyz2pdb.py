import numpy as np
import datetime
import argparse

def read_xyz(filename):
    atoms_lbls = np.loadtxt(filename, usecols=0, skiprows=2, dtype=np.str)
    coords = np.loadtxt(filename, usecols=(1,2,3), skiprows=2)
    charges = np.loadtxt(filename, usecols=4, skiprows=2)
    atoms = np.loadtxt(filename, usecols=5, skiprows=2, dtype=np.str)
    return atoms_lbls, coords, charges, atoms

def create_lists_xyz(listoffiles):
    atoms_lbls_grouped = [ read_xyz(ifile)[0] for ifile in listoffiles ]
    coords_grouped = [ read_xyz(ifile)[1] for ifile in listoffiles ] 
    charges_grouped = [ read_xyz(ifile)[2] for ifile in listoffiles ]
    atoms_grouped = [ read_xyz(ifile)[3] for ifile in listoffiles ]
    return atoms_lbls_grouped, coords_grouped, charges_grouped, atoms_grouped

def main(wholesystem, nc, ligands, n_ligands, solvents, n_solvents):
    # Write pdb file
    cell_size = [75, 75, 75]
    cell_angle = [90, 90, 90]
    title = "TITLE     PDB file created by Ivan \n"
    author = 'AUTHOR    {} {} \n'.format('Ivan Infante', datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
    crystal = 'CRYST1{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}\n'.format(
            cell_size[0], cell_size[1], cell_size[2], cell_angle[0], cell_angle[1], cell_angle[2])

    loop_atoms = title + author + crystal

    # Read the atoms and coordinates of the whole system
    atoms = np.loadtxt(wholesystem, usecols=0, skiprows=2, dtype=np.str) 
    coords = np.loadtxt(wholesystem, skiprows = 2, usecols=(1,2,3)) 

    # Write first the NC
    tot_atoms = 0
    atype = 0 
    if nc:
        atoms_lbls_nc, coords_nc, charges_nc, atoms_nc = create_lists_xyz(nc) # Take info from xyz of fragments, coords are not needed.   
        for atype in range(len(nc)): # Loop over each moiety made of an atom type of the NC, e.g. the Pb moiety
            for iatom in range(len(atoms_nc[atype])):
                tot_atoms += 1
                loop_atoms += 'ATOM{:7d} {:4s}  {:3s}{:5d}    {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}      MOL{:1d}{:2s}\n'.format(
                        tot_atoms, atoms_lbls_nc[atype][iatom], 'R1', tot_atoms,
                        coords[tot_atoms-1,0], coords[tot_atoms-1,1], coords[tot_atoms-1,2], 1,
                        charges_nc[atype][iatom], atype+1, atoms_nc[atype][iatom] ) 
    
    # Now write the ligands. 
    tot_residues = tot_atoms 
    tot_fragtype = atype 
    if ligands: 
        atoms_lbls_lig, coords_lig, charges_lig, atoms_lig = create_lists_xyz(ligands) 
        for ligtype in range(len(ligands)): 
            tot_fragtype += 1
            for ilig in range(int(n_ligands[ligtype])):
                tot_residues += 1 
                for iatom in range(len(atoms_lig[ligtype])):
                     tot_atoms += 1
                     loop_atoms += 'ATOM{:7d} {:4s}  {:3s}{:5d}    {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}      MOL{:1d}{:2s}\n'.format(
                          tot_atoms, atoms_lbls_lig[ligtype][iatom], 'R1', tot_residues,
                          coords[tot_atoms-1,0], coords[tot_atoms-1,1], coords[tot_atoms-1,2], 1,
                          charges_lig[ligtype][iatom], tot_fragtype, atoms_lig[ligtype][iatom])

    # Now write the ligands. 
    if solvents:
        atoms_lbls_solv, coords_solv, charges_solv, atoms_solv = create_lists_xyz(solvents)
        for solvtype in range(len(solvents)):
            tot_fragtype += 1
            for isolv in range(int(n_solvents[solvtype])):
                tot_residues += 1
                for iatom in range(len(atoms_solv[solvtype])):
                     tot_atoms += 1
                     loop_atoms += 'ATOM{:7d} {:4s}  {:3s}{:5d}    {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}      MOL{:1d}{:2s}\n'.format(
                          tot_atoms, atoms_lbls_solv[solvtype][iatom], 'R1', tot_residues,
                          coords[tot_atoms-1,0], coords[tot_atoms-1,1], coords[tot_atoms-1,2], 1,
                          charges_solv[solvtype][iatom], tot_fragtype, atoms_solv[solvtype][iatom])

    output = '{}.pdb'.format(wholesystem) 
    with open(output, 'w') as f:
         f.write(loop_atoms)

def read_cmd_line(parser):
    """
    Parse Command line options.
    """
    args = parser.parse_args()

    attributes = ['whole', 'nc', 'ligands', 'n_ligands', 'solvents', 'n_solvents']

    return [getattr(args, p) for p in attributes]

if __name__ == "__main__":
    msg = "xyz2pdb -nc <path/to/filenames> "

    parser = argparse.ArgumentParser(description=msg)
    parser.add_argument(
        '-whole', required=True, help='path to the xyz file of the entire system: NC + ligands + solvent')
    parser.add_argument(
        '-nc', required=False, nargs='+', help='path to the xyz files of the nanocrystal atomic types')
    parser.add_argument(
        '-ligands', required=False, nargs='+', help='path to the xyz file(s) of the ligand(s) type(s)')
    parser.add_argument(
        '-n_ligands', required=False, nargs='+', help='number of moieties of a given ligand type')
    parser.add_argument(
        '-solvents', required=False, nargs='+', help='path to the xyz file(s) of the solvent(s) type(s)')
    parser.add_argument(
        '-n_solvents', required=False, nargs='+', help='number of moieties of a given solvent type')
    main(*read_cmd_line(parser))

