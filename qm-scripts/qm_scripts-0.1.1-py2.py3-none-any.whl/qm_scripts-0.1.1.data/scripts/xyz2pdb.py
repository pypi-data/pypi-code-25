#!python
# -*- coding: utf-8 -*-
"""
Created on Wed May  2 19:26:20 2018
 
@author: Ivan Infante 
"""
import numpy as np
import datetime
 
charges = {
        "Cs": 1.000,
        "Pb": 2.000,
        "Br": -1.000,
        "NG3P": -0.590,
        "HGP5": 0.250,
        "HGA2": 0.090,
        "HGA3": 0.090,
        "CG21": -0.180,
        "CG24": -0.104,
        "CG31": -0.270,
        "CG34": -0.349,
        }
 
# Read a file of ligand with atomic labels as in the force field file. Warning: the atom labels need to be listed as the original ligand
file_lig_label = 'DDAB_label_final.xyz'
atoms_lig_label = np.loadtxt(file_lig_label, usecols=0, dtype=np.str) # Read file of ligands with label
n_atoms_lig = atoms_lig_label.size # Number of atoms in the ligand
 
# Read xyz file
# Note: in the xyz file the atoms of the NC are listed first, then the atoms of the ligand.
# If there is more than one ligand of the same type, the atoms of ligand1 are stacked first, then the second, etc.
# Each ligand must follow the same atomic order of the first ligand stacked after the NC.
n_atoms_NC = 393 # Number of atoms of the core Nanocrystal
n_ligands = 23 # Number of ligands of same type
name_lig = 'DDA' # Maximum 3 characters
 
filename = 'CsPbBr3_23DDAB.xyz' # Name of xyz file
atoms = np.loadtxt(filename, skiprows=2, usecols=0, dtype=np.str) # Read atoms names from xyz file
coords = np.loadtxt(filename, skiprows=2, usecols=(1,2,3)) # Read coordinates of all atoms
 
# Write pdb file
cell_size = [75, 75, 75]
cell_angle = [90, 90, 90]
title = "TITLE     PDB file created by Ivan \n"
author = 'AUTHOR    {} {} \n'.format('Ivan Infante', datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
crystal = 'CRYST1{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}{:9.3f}\n'.format(
        cell_size[0], cell_size[1], cell_size[2], cell_angle[0], cell_angle[1], cell_angle[2])          
 
loop_atoms = title + author + crystal
# Write first the NC
for iatom in range(n_atoms_NC):  
     loop_atoms += 'ATOM{:7d} {:4s}  {:3s}{:5d}    {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}      {:4s}{:2s}\n'.format(
             iatom+1, atoms[iatom], 'R1', iatom+1, coords[iatom,0], coords[iatom,1], coords[iatom,2], 1, charges[atoms[iatom]], 'CPB', atoms[iatom])
 
# Now write the ligands
for ilig in range(n_ligands):
    res = 'R{}'.format(ilig+2)
    for iatom in range(n_atoms_lig):
        loop_atoms += 'ATOM{:7d} {:4s}  {:3s}{:5d}    {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}      {:4s}{:2s}\n'.format(
                (iatom + n_atoms_lig * ilig + n_atoms_NC + 1), atoms_lig_label[iatom], res, n_atoms_NC+ilig+1,
                coords[iatom + n_atoms_lig * ilig + n_atoms_NC,0], coords[iatom + n_atoms_lig * ilig + n_atoms_NC,1], coords[iatom + n_atoms_lig * ilig + n_atoms_NC,2],
                1, charges[atoms_lig_label[iatom]], name_lig, atoms[iatom+n_atoms_NC])
 
with open('result.pdb', 'w') as f:
    f.write(loop_atoms)

