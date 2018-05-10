"""Example: using ymlref with document in str."""
from io import StringIO
import ymlref


DOCUMENT = """

authors:
  shakespear:
    first_name: William
    last_name: Shakespear
  dostoevsky:
    first_name: Fyodor
    last_name: Dostoevsky
books:
   - title: Makbet
     author:
       $ref: "#/authors/shakespear"
   - title: Crime and punishment
     author:
       $ref: "#/authors/dostoevsky"
"""


def main():
    """Entrypoint for this example."""
    doc = ymlref.loads(DOCUMENT)
    print('Books in document: \n')
    for book in doc['books']:
        print(book['title'])
        print('Author: ' + book['author']['first_name'] + ' ' + book['author']['last_name'])
        print('---')

if __name__ == '__main__':
    main()
