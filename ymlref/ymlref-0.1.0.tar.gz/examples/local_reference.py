"""Example: using ymlref, resolving references to local file."""
from io import StringIO
import ymlref


DOCUMENT_1 = """
db_name: people
content:
  $ref: ./people.yml
"""

DOCUMENT_2 =  """
db_name: people
content:
  $ref: people.yml
"""


def main():
    """Entrypoint for this example."""
    doc = ymlref.loads(DOCUMENT_1)
    print('People in DB: ')
    for person in doc['content']:
        print(person['first_name'] + ' ' + person['last_name'])

    doc2 = ymlref.loads(DOCUMENT_2)
    print('People in DB: ')
    for person in doc2['content']:
        print(person['first_name'] + ' ' + person['last_name'])

if __name__ == '__main__':
    main()
