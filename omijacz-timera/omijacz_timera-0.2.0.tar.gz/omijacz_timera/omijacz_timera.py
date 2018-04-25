"""Uruchamia automatyzację slajdów na prawojazdy.com.pl

Usage:
  omijacz_timera
  omijacz_timera (-h | --help)
  omijacz_timera --version
  omijacz_timera -v

Options
  -h --help  pokaż pomoc (o taką!)
  -version  wersja
  -v  wyświetlaj więcej tekstu (verbose)
"""

from __future__ import division, print_function, absolute_import

import datetime
import time

from docopt import docopt

import omijacz_timera.automator as automator
import omijacz_timera.automator_api as automator_api

__version__ = "0.1"
__author__ = "Jonatan Witoszek"
__copyright__ = "Jonatan Witoszek"
__license__ = "MIT"

def execute():
    strona = automator.Prawojazdy()
    # Logowanie i wybieranie kursu
    strona.zaloguj_sie()
    while not strona.zalogowano():
        continue
    print("Przejdź do nauki i wybierz kurs...")
    while not strona.kurs_wybrany():
        continue
    # Tworzenie klasy dla API
    cookies = strona.find_cookies()
    url = strona.get_url()
    ajax = automator_api.Prawojazdy_API(cookies, url)
    ajax_header = ajax.get_header()
    # Pętla zaliczania slajdów
    while not strona.check_if_ended():
        # Sprawdzenie czy nie pytanie TODO: Temporary fix
        if strona.check_if_not_question():
            strona.nastepna_strona()
            continue
        # Odczytywanie danych ze strony
        slide_numer = strona.find_slide_number()
        if slide_numer == "0":
            strona.nastepna_strona()
        # Tworzenie i przekazywanie zapytania AJAX
        content = ajax.get_content(slide_numer)
        if not ajax.send_request(content, ajax_header):
            print("Niepowodzenie zapytania. Próbuję jeszcze raz...")
            time.sleep(5)
            ajax.send_request(content, ajax_header)
            strona.browser.reload()
        time.sleep(2.5)
        # Przechodzenie do następnej strony
        strona.nastepna_strona()
    strona.zamknij_strone()

def main():
    args = docopt(__doc__)
    # Arguments handling
    if args['--version']:
        print("""omijacz-timera-prawojazdy wersja {version}
        Created by {author}
        Copyright Jonatan Witoszek - {year} {licence}""".format(
            version=__version__,
            author=__author__,
            year=datetime.datetime.now().year,
            licence=__license__
        ))
    VERBOSE = args['-v'] or False #  Todo: Add verbose messages
    execute()

if __name__ == "__main__":
    main()