from bs4 import BeautifulSoup
import requests
import csv


def main():
    tip = input("Da li tražite stan na prodaju ili na iznajmljivanje?\n1.Kupovina, 2.Iznajmljivanje")
    if int(tip) == 1:
        tip_rec = 'prodaja'
    else:
        tip_rec = 'najam'
    naselje = input("Unesite ime naselja: ")
    opstina = input("Unesite ime opštine: ")
    tip_nekretnine = input("Izaberite broj tipa nekretnine tako što ćete ukucati:\n 1.kuća, 2. stan, 3.apartman, "
                           "4. poslovni prostor, 5. zemljište, 6. garaža")
    cena_min = input("Minimalna cena nekretnine: ")
    cena_max = input("Maksimalna cena nekretnine: ")
    povrsina_min = input("Minimalna kvadratura: ")
    maksimalna_kvadratura = input("Maksimalna kvadratura: ")
    page_num = 0

    while not isinstance(int(tip_nekretnine), int):
        tip_nekretnine = input("Izaberite tip nekretnine tako što ćete ukucati:\n 1.kuća, 2. stan, 3.apartman, "
                               "4. poslovni prostor, 5. zemljište, 6. garaža")

    while not isinstance(int(cena_min), int):
        cena_min = input("Minimalna cena nekretnine: ")

    while not isinstance(int(cena_max), int):
        cena_max = input("Maksimalna cena nekretnine: ")

    while not isinstance(int(povrsina_min), int):
        povrsina_min = input("Minimalna kvadratura: ")

    while not isinstance(int(maksimalna_kvadratura), int):
        maksimalna_kvadratura = input("Maksimalna kvadratura: ")

    finished = False

    with open('real_estates_in_Belgrade.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['price', 'location', 'size', 'link'])

        while not finished:

            page_num += 1

            url = f'http://www.adventisrealestate.com/pretraga/{tip_rec}-{tip}/tip-{tip_nekretnine}/tekst-{naselje},' \
                  f'{opstina} (Beograd)/cena_max-{cena_max}/cena_min-{cena_min}/povrsina_max-' \
                  f'{maksimalna_kvadratura}/povrsina_min-' \
                  f'{povrsina_min}/stranica-{page_num} '

            response = requests.get(url)

            soup = BeautifulSoup(response.text, 'html.parser')

            for offer in soup.findAll('div', {'class': 'col-xxs-12 col-xs-6 col-sm-12'}):
                price = offer.find('div', {'class': 'realestateItemInfo'}).find('div', {'class': 'prices'}) \
                    .find('h3', {'class': 'price'}).contents[0].strip()

                try:
                    location = \
                        offer.find('div', {'class': 'realestateItemInfo'}) \
                            .find('div', {'class': 'pull-left description'}) \
                            .find('div', {'class': 'data'}).findAll('p', {'class': 'info'})[1].contents[2].strip()
                except IndexError:
                    location = ''

                size = offer.find('div', {'class': 'realestateItemInfo'}) \
                    .find('div', {'class': 'col-xs-12 realestateDetails'}).find('span',
                                                                                {'class': 'infoCount'}).contents[
                    0].strip()

                link = offer.find('div', {'class': 'realestateItemInfo'}).find('a', {'class': 'title'})['href']

                location = location.replace('Å', '')
                location = location.replace('¾', 'ž')
                location = location.replace('Ä', '')
                location = location.replace(u'\x87', 'ć')
                location = location.replace(u'\x8d', 'č')
                location = location.replace(u'\x91', 'đ')
                location = location.replace('\x8c', 'Č')
                location = location.replace('½', 'Ž')
                print(price, location, size, link)

                csv_writer.writerow([price, location, size, link])

                if soup.find('li', {'class': 'next'}) is None:
                    finished = True


if __name__ == '__main__':
    main()
