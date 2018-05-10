"""Example: using jsonpointer with ymlref."""
from jsonpointer import resolve_pointer
import ymlref


DOCUMENT = """
pokemon:
  pikachu:
    species: Pikachu
    number: 25
    type: electric
  bulbasaur:
    species: Bulbasaur
    number: 1
    type: grass
  squirtle:
    species: Squirtle
    number: 7
    type: water
my:
  - name: Buzz
    type: #/pokemon/pikachu
    level: 15
  - name: Sparky
    type: #/pokemon/pikachu
    level: 25
  - name: Leaf
    type: #/pokemon/bulbasaur
    level: 10
"""

def main():
    """Entrypoint for this example."""
    doc = ymlref.load(DOCUMENT)
    levels = [resolve_pointer(doc, '/my/{}/level'.format(i)) for i in range(len(doc['my']))]
    print('Levels of my pokemon: {}'.format(levels))
    print('Pikachu is of type: ' + resolve_pointer(doc, '/pokemon/pikachu/type'))


if __name__ == '__main__':
    main()
