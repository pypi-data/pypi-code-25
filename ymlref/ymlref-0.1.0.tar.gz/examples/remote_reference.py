"""Example: using ymlref, resolving references to remote document."""
from io import StringIO
import ymlref


DOCUMENT = """
db_name: people
content:
  $ref: https://raw.githubusercontent.com/dexter2206/ymlref/feature/external-references/examples/people.yml
"""


def main():
    """Entrypoint for this example."""
    doc = ymlref.loads(DOCUMENT)
    print('People in DB: ')
    for person in doc['content']:
        print(person['first_name'] + ' ' + person['last_name'])


if __name__ == '__main__':
    main()
