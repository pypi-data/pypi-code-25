"""
Dans_Diffraction Tests
Check reading of cif files
"""


import Dans_Diffraction as dif

files = list(dif.classes_structures.cif_list())
files += [r"C:\Users\grp66007\Downloads\1000175.cif"]

for file in files:
    xtl = dif.Crystal(file)
    N = len(xtl.Structure.type) # atoms in unit cell
    I = xtl.Scatter.intensity([1,0,0]) # intensity of reflection
    print('%30s N=%3.0f I=%8.2f'%(xtl.name, N, I))