# -*- coding: utf-8 -*-
""" Read a source database containg reuses in a corpus, then save them the
useful informations into a SQLite3 database.

The source database is usually the one outputed by the text-align software
(located at https://github.com/ARTFL-Project/text-align), but any CSV file
properly configured can be used.
"""

import codecs
import re

from progressbar import ProgressBar, Percentage, Counter, Timer

import galaxies.src.core.database_tools as db
from galaxies.src.common.file import line_count


PB_WIDGETS = ["Processed: ", Counter(), " lines [", Percentage(), "], ",
              Timer()]

MESSAGE_REUSES_RODE = "{} reuses rode from the source file."


def parse_reuse_file(database_source: str, database_dest: str,
                     max_book_to_add: int, delimiter: str, encoding: str,
                     header: bool, index_src_author: int, index_src_title: int,
                     index_src_date: int, index_src_text_matched: int,
                     index_src_start_byte: int, index_src_end_byte: int,
                     index_dest_author: int, index_dest_title: int,
                     index_dest_date: int, index_dest_text_matched: int,
                     index_dest_start_byte: int, index_dest_end_byte: int):
    """ Read a source database containg reuses in a corpus, then save the
    useful informations into a SQLite3 database.

    The source database is usually the one outputed by the text-align software
    (located at https://github.com/ARTFL-Project/text-align), but any CSV file
    properly configured can be used.
    """
    # Set the number of lines to read for the progress bar
    if max_book_to_add < 0:
        max_book_to_add = line_count(database_source)

    connexion = db.connexion(database_dest)
    curseur = connexion.cursor()
    with codecs.open(database_source, 'r', encoding, errors='replace') as file:
        if header:
            # Remove the header
            file.readline()

        progress_bar = ProgressBar(widgets=PB_WIDGETS, maxval=max_book_to_add)
        progress_bar.start()
        for line_number, line in enumerate(file):
            if line_number == max_book_to_add:
                break

            l = re.split(delimiter, line)
            # Add the two books into the database (do nothing if one of them is
            # already present).
            db.add_book(l[index_src_author],
                        l[index_src_title],
                        l[index_src_date], curseur)
            db.add_book(l[index_dest_author],
                        l[index_dest_title],
                        l[index_dest_date], curseur)

            # Retrieve the identifier of the two books (because the two of them
            # may be already present).
            id_src = db.get_id_book(l[index_src_author],
                                    l[index_src_title],
                                    l[index_src_date],
                                    curseur)
            id_dest = db.get_id_book(l[index_dest_author],
                                     l[index_dest_title],
                                     l[index_dest_date],
                                     curseur)

            # Add a reuse for the source book and the destination book
            real_id_book_source = db.id_ref(l[index_src_author], l[index_src_title], l[index_src_date])
            real_id_book_target = db.id_ref(l[index_dest_author], l[index_dest_title], l[index_dest_date])
            db.add_reuse(id_src,
                         int(l[index_src_start_byte]),
                         int(l[index_src_end_byte]) -
                         int(l[index_src_start_byte]),
                         l[index_src_text_matched],
                         id_dest,
                         int(l[index_dest_start_byte]),
                         int(l[index_dest_end_byte]) -
                         int(l[index_dest_start_byte]),
                         l[index_dest_text_matched],
                         real_id_book_source,
                         real_id_book_target,
                         curseur)
            progress_bar.update(line_number + 1)

    progress_bar.finish()
    connexion.commit()
    connexion.close()

    print(MESSAGE_REUSES_RODE.format(max_book_to_add))


if __name__ == '__main__':
    pass
