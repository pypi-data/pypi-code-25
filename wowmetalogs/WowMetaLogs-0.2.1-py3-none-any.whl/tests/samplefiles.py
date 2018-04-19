# Imports

import json
from apis.blizzapi import BlizzAPI
blizz_api = BlizzAPI('j2g3d863c73ujzd2jdc8dfg73m75zr4g')

# Guild
with open('guild.txt', 'w') as file:
    json.dump(blizz_api.get_guild('proudmoore', 'firehawk'), file, indent=4)

# Character
with open('char.txt', 'w') as file:
    json.dump(blizz_api.get_character('proudmoore', 'piousbob'), file, indent=4)

# Item
with open('item.txt', 'w') as file:
    json.dump(blizz_api.get_item(152158), file, indent=4)
