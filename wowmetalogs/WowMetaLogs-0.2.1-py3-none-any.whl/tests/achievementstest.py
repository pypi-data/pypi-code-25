import json
import sys
from apis.blizzapi import BlizzAPI

blizz = BlizzAPI('j2g3d863c73ujzd2jdc8dfg73m75zr4g')

json.dump(blizz.get_character('proudmoore', 'piousbob'), sys.stdout)
