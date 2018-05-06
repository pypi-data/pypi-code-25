"""
Context
-------
LUCA has previously been derived from various methods. This is a method of creating a LUCA using only annotated genomes from KEGG. It is expected to be far less precise than methods carefully crafted by experts.
Furthermore, this experiment is limited to the common ancestor of Archaea, Bacteria, and Archaea+Bacteria; Eukaryota are not in the scope of this work and, thus, the truley universal LUCA is not.

Question
--------
How many EC numbers are shared among Archaea, Bacteria, and Archaea+Bacteria?
Including the ones from multifunctional enzymes.

Method
------
- REPEAT for each clade in Archaea, Bacteria, Archaea+Bacteria
-     get collective metabolism of clade
-     REPEAT for varying majority percentages
-         calculate core metabolism
-         print number of ECs by majority percentage
-         IF majority percentage is 100%, i.e. consensus, also print the ECs

Result
------

::

    Archaea-KeggLUCA
    100% ECs: 8 (2.7.7.6, 2.7.4.3, 2.7.7.7, 6.3.5.7, 6.1.1.21, 6.1.1.2, 6.1.1.4, 6.1.1.20)
    90% ECs: 101
    80% ECs: 152
    70% ECs: 207
    60% ECs: 241
    50% ECs: 293
    40% ECs: 328
    30% ECs: 400
    20% ECs: 460
    10% ECs: 603
    
    
    Bacteria-KeggLUCA
    100% ECs: 1 (2.7.7.7)
    90% ECs: 86
    80% ECs: 179
    70% ECs: 262
    60% ECs: 329
    50% ECs: 394
    40% ECs: 472
    30% ECs: 582
    20% ECs: 720
    10% ECs: 969
    
    
    Archaea-Bacteria-KeggLUCA
    100% ECs: 1 (2.7.7.7)
    90% ECs: 70
    80% ECs: 164
    70% ECs: 255
    60% ECs: 321
    50% ECs: 388
    40% ECs: 466
    30% ECs: 571
    20% ECs: 708
    10% ECs: 965

Conclusion
----------
There are many EC numbers shared among all species of the Archaea, Bacteria, and even the combination of both clades.
Even when defining 'core metabolism' by consensus, 2.7.7.7 occurs in all organisms.

However, this approach suffers harshly from incomplete annotations, not only resulting in one less count of an EC number which should have occured, but also resulting in a decreased chance of occuring within a fixed majority threshold.
"""
from FEV_KEGG.KEGG.LUCA import KeggLUCA

if __name__ == '__main__':
    
    output = []
    
    #- REPEAT for each clade in Archaea, Bacteria, Archaea+Bacteria
    for clade in [KeggLUCA.CladeType.archaea, KeggLUCA.CladeType.bacteria, KeggLUCA.CladeType.archaeaBacteria]:
        
        #-     get collective metabolism of clade
        luca = KeggLUCA(clade)
        output.append(luca.nameAbbreviation)
        
        #-     REPEAT for varying majority percentages
        for percentage in range(100, 0, -10):
            
            #-         calculate core metabolism
            ecNumbers = luca.substrateEcGraph( percentage ).getECs()
            
            #-         print number of ECs by majority percentage
            if percentage == 100:
                #-         IF majority percentage is 100%, i.e. consensus, also print the ECs
                output.append( str(percentage) + "% ECs: " + str(len( ecNumbers )) + " (" + ", ".join([str(x) for x in ecNumbers]) + ")")
            else:
                output.append( str(percentage) + "% ECs: " + str(len( ecNumbers )) )
            
        output.append("\n")
        
        luca.clade.group.freeHeap()
        luca = None
    
    for line in output:
        print(line)
