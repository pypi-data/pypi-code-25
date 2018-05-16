__all__ = ['make_bond_matrix', 'rdf']

import numpy as np 
import subprocess

def make_bond_matrix(n_atoms, coords):
    #Build a tensor made (n_atoms, axes, n_atoms), where axes = x-x0, y-y0, z-z0
    dist = np.stack(
            np.stack(
                    (coords[i_atm, i_ax] - coords[:, i_ax]) ** 2 for i_ax in range(coords.shape[1])
                    )
            for i_atm in range(n_atoms)
            )
    # Builds the bond distance matrix between atoms 
    r = np.stack(
            np.sqrt(np.sum(dist[i_atm, :, :], axis=0)) for i_atm in range(n_atoms)
            )
    return r

def rdf(fn, atoms_i, atoms_j, dr, rmax, start, stride): 
    # Retrieve number of lines in trajectory file
    cmd = "wc -l {}".format(fn)
    l = subprocess.check_output(cmd.split()).decode()
    n_lines = int(l.split()[0]) # Number of lines in traj file

    # Read number of atoms in the molecule. It is usually the first line in a xyz file  
    with open(fn) as f:
       l = f.readline()
       n_atoms = int(l.split()[0])

    # Calculate total number of frames in the trajectory file  
    n_frames = int(int(n_lines)/(n_atoms+2))
    
    # Create grid of r values to compute the pair correlation function g_ij 
    r_grid = np.arange(0, rmax, dr)
    
    # Compute the volume in a concentric sphere of size dr at a distance r from the origin  
    volume = 4 * np.pi * np.power(r_grid, 2) * dr # elemental volume dV = 4*pi*r^2*dr

    # Read the order of atoms from the first frame of the trajectory. This order is unchanged. 
    atoms = np.genfromtxt(fn, skip_header = 2, skip_footer=(int(n_lines) - (n_atoms + 2)), usecols=0, dtype=str)

    # Find the indexes in the bond_matrix of the atomic types involved in the calculation of g_ij
    index_i = np.where( atoms == atoms_i )
    index_j = np.where( atoms == atoms_j )

    for iframe in range(start, n_frames, stride): 
        # Read coordinates from iframe
        coords = np.genfromtxt(fn, skip_header = (2 + (n_atoms + 2) * (iframe - 1)), 
                    skip_footer=(int(n_lines) - ((n_atoms + 2) * iframe)), usecols=(1,2,3))
        # Compute bond distance matrix for iframe
        bond_mtx = make_bond_matrix(n_atoms, coords)
        # Slice the bond_matrix with only the atom types
        sliced_mtx = bond_mtx[np.ix_(index_i[0], index_j[0])]
        # Count the number of atoms within r and r+dr  
        counts = np.stack( np.where( (sliced_mtx > r_grid[idr]) & (sliced_mtx < r_grid[idr+1]) )[0].size for idr in range(r_grid.size-1))
        # Compute the density of atoms inside r and r+dr the elemental volume dV 
        density = counts / volume[1:] # skip the first element dV which is 0 
        # Store density in g_ij
        if (iframe == start):
            g_ij = density
        else:
            g_ij = np.column_stack((g_ij,density))

    # Average over all frames
    g_ij_av = np.average(g_ij, axis=1)

    return r_grid[1:], g_ij_av 



