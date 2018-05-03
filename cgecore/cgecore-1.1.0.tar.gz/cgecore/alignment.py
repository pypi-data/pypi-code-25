#!/usr/bin/env python3
""" This module contains core functions and classes related to alignment. """
################################################################################
#                             CGE ALIGNMENT MODULE                             #
################################################################################

def extended_cigar(aligned_template, aligned_query):
   ''' Convert mutation annotations to extended cigar format
   
   https://github.com/lh3/minimap2#the-cs-optional-tag
   
   USAGE:
      >>> template = 'CGATCGATAAATAGAGTAG---GAATAGCA'
      >>> query = 'CGATCG---AATAGAGTAGGTCGAATtGCA'
      >>> extended_cigar(template, query) == ':6-ata:10+gtc:4*at:3'
      True
   '''
   #   - Go through each position in the alignment
   insertion = []
   deletion = []
   matches = []
   cigar = []
   for r_aa, q_aa in zip(aligned_template.lower(), aligned_query.lower()):
      gap_ref = r_aa == '-'
      gap_que = q_aa == '-'
      match = r_aa == q_aa
      if matches and not match:
         # End match block
         cigar.append(":%s"%len(matches))
         matches = []
      if insertion and not gap_ref:
         # End insertion
         cigar.append("+%s"%''.join(insertion))
         insertion = []
      elif deletion and not gap_que:
         # End deletion
         cigar.append("-%s"%''.join(deletion))
         deletion = []
      if gap_ref:
         if insertion:
            # Extend insertion
            insertion.append(q_aa)
         else:
            # Start insertion
            insertion = [q_aa]
      elif gap_que:
         if deletion:
            # Extend deletion
            deletion.append(r_aa)
         else:
            # Start deletion
            deletion = [r_aa]
      elif match:
         if matches:
            # Extend match block
            matches.append(r_aa)
         else:
            # Start match block
            matches = [r_aa]
      else:
         # Add SNP annotation
         cigar.append("*%s%s"%(r_aa, q_aa))
   
   if matches:
      cigar.append(":%s"%len(matches))
      del matches
   if insertion:
      # End insertion
      cigar.append("+%s"%''.join(insertion))
      del insertion
   elif deletion:
      # End deletion
      cigar.append("-%s"%''.join(deletion))
      del deletion
   
   return ''.join(cigar)
