import os
import collections
import csv


SearchResult = collections.namedtuple('SearchResult',
                                      'file, line, text')


def main():
    print_header()
    folder = get_folder_or_file()
    if not folder:
        print("Invalid search location")
        return

    text = get_search_text()
    if not text:
        print("Invalid search input")
        return
    if os.path.isdir(folder):
        matches = search_folders(folder, text)
    else:
        matches = search_file(folder, text)
    total_matches = 0
    with open('matches_in_text.csv', 'w') as csv_file:

        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['source_file', 'line_number_in_which_match_was_found', 'line_in_which_match_was_found'])

        for match in matches:
            print('----------MATCH----------')
            print('file: ' + match.file)
            print('line: ' + match.line)
            print('match: ' + match.text.rstrip())
            print()
            csv_writer.writerow([match.file, match.line, match.text.rstrip()])
            total_matches += 1
        print(f"Total number of found matches: {total_matches}")


def print_header():
    print('-------------------------------------')
    print('           FILE SEARCH APP           ')
    print('-------------------------------------')


def get_folder_or_file():
    folder = input(
        'What folder or a specific file do you want to search?\nPlease enter a full path to folder or a file: ')
    if not folder or not folder.strip():
        return None

    if not os.path.isdir(folder):
        return os.path.abspath(folder)

    return os.path.abspath(folder)


def get_search_text():
    text = input("What word or expression are you searching for? ")
    return text.lower()


def search_file(full_item, text):
    with open(full_item, 'r', encoding='latin-1') as f:
        for count, line in enumerate(f):
            if line.lower().find(text) >= 0:
                m = SearchResult(line=str(count+1), file=full_item, text=line)
                yield m


def search_folders(folder, text):
    items = os.listdir(folder)
    for item in items:
        full_item = os.path.join(folder, item)
        if os.path.isdir(full_item):
            yield from search_folders(full_item, text)
        else:
            yield from search_file(full_item, text)


if __name__ == '__main__':
    main()
