from bs4 import BeautifulSoup
import requests
import csv
import time


def main():
    lista_mogucih_drzava = ['Hrvatska', 'Bosna-I-Hercegovina', 'Crna-Gora', 'Srbija']
    drzava = input("Unesite željenu državu za pretragu. Mogući izbori su:\nHrvatska\nSrbija\nBosna i "
                   "Hercegovina\nCrna Gora\n").title().replace(' ', '-')
    while drzava not in lista_mogucih_drzava:
        drzava = input("Unesite željenu državu za pretragu. Mogući izbori su:\nHrvatska\nSrbija\nBosna i "
                       "Hercegovina\nCrna Gora\n").title().replace(' ', '-')
    base_url = f'https://www.realitica.com/nekretnine/{drzava}/'
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    if drzava == 'Hrvatska':
        div_id = 'xc378'
    elif drzava == 'Srbija':
        div_id = 'xc393'
    elif drzava == 'Bosna-I-Hercegovina':
        div_id = 'xc953'
    else:
        div_id = 'xc241'
    drzava = drzava.replace('-', '+')
    print('\n')
    for location in soup.find('div', {'id': div_id}).findAll('div', {'id': 'search_col2_full'}):
        name_of_the_location = location.span.a.contents[0]
        print(name_of_the_location)
    for location in soup.find('div', {'id': div_id}).findAll('div', {'id': 'search_col2_half'}):
        name_of_the_location = location.span.a.contents[0]
        print(name_of_the_location)
    grad = input('Unesite željeni grad za pretragu. Mogući izbori su izlistani iznad: ')
    opstina = input('\nDubrovnik-Neretva\nSplit-Dalmacija\nZadarska\nPrimorje-Gorski '
                    'Kotar\nIstra\nZagreb\nBeograd\nNovi Sad\nSarajevo\nBanja Luka\nHerceg Novi\nPodgorica\nUkoliko je '
                    'izabrani grad među grupom od ovih 12 gradova, ovde možete uneti ime opštine kako biste suzili '
                    'pretragu, ako to nije slucač ostavite polje prazno: ')
    opstina.replace(' ', '+')
    lista_mogucih_tipova_nekretnina = ['kuća', 'stan', 'zemljište', 'poslovni prostor', 'hotel',
                                       'građevinsko zemljište', 'poljoprivredno zemljište']
    tip_nekretnine = input('Izaberite tip nekretnine: kuća\nstan\nzemljište\nposlovni prostor\nhotel\ngrađevinsko '
                           'zemljište\npoljoprivredno zemljište\n')
    while tip_nekretnine not in lista_mogucih_tipova_nekretnina:
        tip_nekretnine = input('Izaberite tip nekretnine: kuća\nstan\nzemljište\nposlovni prostor\nhotel\ngrađevinsko '
                               'zemljište\npoljoprivredno zemljište\n')
    minimalna_cena = input('Unesite minimalnu cenu nekretnine: ')
    maksimalna_cena = input('Unesite maksimalnu cenu nekretnine: ')
    timeout_timer = time.time() + 5
    page_id = 0
    if tip_nekretnine == 'kuća':
        tip_nekretnine = 'Home'
    elif tip_nekretnine == 'stan':
        tip_nekretnine = 'Apartment'
    elif tip_nekretnine == 'zemljište':
        tip_nekretnine = 'Land'
    elif tip_nekretnine == 'poslovni prostor':
        tip_nekretnine = 'Commercial'
    elif tip_nekretnine == 'građevinsko zemljište':
        tip_nekretnine = 'Residential_lot'
    elif tip_nekretnine == 'poljoprivredno zemljište':
        tip_nekretnine = 'Agricultural_land'

    finished = False

    with open('real_estates_in.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['price', 'size', 'location', 'link'])

        link = ''
        while not finished:

            if opstina:
                base_url = f'https://www.realitica.com/?cur_page={page_id}&for=Prodaja&opa%5B%5D={opstina}&pZpa=' \
                           f'{grad}&pState=' \
                           f'{drzava}&type%5B%5D={tip_nekretnine}&price-min={minimalna_cena}&price-max=' \
                           f'{maksimalna_cena}&qry=&lng=hr '
            else:
                base_url = f'https://www.realitica.com/?cur_page={page_id}&for=Prodaja&pZpa={grad}&pState=' \
                           f'{drzava}&type%5B%5D={tip_nekretnine}&price-min={minimalna_cena}&price-max=' \
                           f'{maksimalna_cena}&qry=&lng=hr '

            response = requests.get(base_url)

            soup = BeautifulSoup(response.text, 'html.parser')

            if not (soup.findAll('div',
                                 {'style': 'padding:15px 10px;clear:both;white-space: normal; overflow: hidden; '
                                           'text-overflow: ellipsis; border: 1px solid #ccc; background:#fff9dd;'})) \
                    and not soup.findAll('div',
                                         {
                                             'style': 'padding:15px 10px;clear:both;white-space: normal; overflow: '
                                                      'hidden; '
                                                      'text-overflow: ellipsis; border: 1px solid #ccc; '}):
                base_url = f'https://www.realitica.com/?cur_page={page_id}&for=Prodaja&opa={grad}&cty%5B%5D=' \
                           f'{opstina}&type%5B%5D={tip_nekretnine}&price-min={minimalna_cena}&' \
                           f'price-max={maksimalna_cena}&qry=&lng=hr '

            response = requests.get(base_url)

            soup = BeautifulSoup(response.text, 'html.parser')

            for offer in soup.findAll('div',
                                      {'style': 'padding:15px 10px;clear:both;white-space: normal; overflow: hidden; '
                                                'text-overflow: ellipsis; border: 1px solid #ccc; background:#fff9dd;'}):
                place = ''
                try:
                    price = offer.findAll('div')[2].findAll('strong')[1].contents[0]
                except IndexError:
                    price = 'No listed price'
                    place = offer.findAll('div')[2].contents[8].strip()
                if not place:
                    try:
                        place = offer.findAll('div')[2].contents[10].strip()
                    except TypeError:
                        try:
                            place = offer.findAll('div')[2].contents[6].strip()
                        except TypeError:
                            place = offer.findAll('div')[2].contents[7].strip()

                link = offer.findAll('div')[2].a['href']
                try:
                    square_meters = offer.findAll('div')[2].contents[4].strip()
                except TypeError:
                    square_meters = 'No information about size'
                print(price, square_meters, place, link)

                csv_writer.writerow([price, square_meters, place, link])

            for offer in soup.findAll('div',
                                      {'style': 'padding:15px 10px;clear:both;white-space: normal; overflow: hidden; '
                                                'text-overflow: ellipsis; border: 1px solid #ccc; '}):
                place = ''
                try:
                    price = offer.findAll('div')[2].findAll('strong')[1].contents[0]
                except IndexError:
                    price = 'No listed price'
                    place = offer.findAll('div')[2].contents[8].strip()
                if not place:
                    try:
                        place = offer.findAll('div')[2].contents[10].strip()
                    except TypeError:
                        place = offer.findAll('div')[2].contents[7].strip()
                try:
                    square_meters = offer.findAll('div')[2].contents[4].strip()
                except TypeError:
                    square_meters = 'No information about size'
                link = offer.findAll('div')[2].a['href']
                print(price, square_meters, place, link)

                csv_writer.writerow([price, square_meters, place, link])

            try:
                href = soup.find('tr').findAll('td')[-1].span
                if href:
                    finished = True
            except TypeError:
                pass
            except AttributeError:
                pass

            if page_id >= 100:
                finished = True
            page_id += 1

            if time.time() > timeout_timer and not link:
                print('Greška pri unosu parametara za pretragu. Pokušajte ponovo i proverite da li su ime grada i '
                      'opštine(pod uslovom da je uneta) pravilno napisani\n')
                break


if __name__ == '__main__':
    main()
