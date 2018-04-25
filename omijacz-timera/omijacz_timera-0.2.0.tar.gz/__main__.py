import time

import omijacz_timera as automator
import omijacz_timera as automator_api

TIMER = 0

if __name__ == "__main__":
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
        # Odczytywanie danych ze strony
        slide_numer = strona.find_slide_number()
        # Tworzenie i przekazywanie zapytania AJAX
        content = ajax.get_content(slide_numer)
        if not ajax.send_request(content, ajax_header):
            print("Niepowodzenie zapytania. Próbuję jeszcze raz...")
            time.sleep(5)
            ajax.send_request(content, ajax_header)
            # strona.browser.reload()
        # time.sleep(2.5*TIMER)
        #  Przechodzenie do następnej strony
        strona.nastepna_strona()
    strona.zamknij_strone()
