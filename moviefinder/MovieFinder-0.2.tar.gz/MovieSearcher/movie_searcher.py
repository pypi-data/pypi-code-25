import shutil
import os
import collections

import requests
import requests.exceptions

MovieResult = collections.namedtuple('MovieResult', 'Title, Year, imdbID, Type, Poster')
api_key = 'a7eeee03'
path = os.path.dirname(os.path.realpath(__file__))


def find_movies(search_term):

    if not search_term.strip():
        raise ValueError("Search text can not be left empty")

    title_url = f'http://www.omdbapi.com/?apikey={api_key}&s={search_term}'

    response = requests.get(title_url)

    json_response = response.json()

    movies_dict = json_response.get('Search')

    movies = [MovieResult(**movie) for movie in movies_dict]

    movies.sort(key=lambda m: -int(m.Year.split('–')[0]))

    return movies


def print_header():
    print('--------------------------------------')
    print('           MOVIE SEARCH APP           ')
    print('--------------------------------------')


def search_movie_loop():
    search_term = 'default'

    while search_term != 'x':
        try:
            search_term = input('Enter the name of the movie you are looking for or type "x" to exit: ')
            if search_term == 'x':
                continue
            movies = find_movies(search_term)
            if search_term not in os.listdir(path):
                os.mkdir(f'{search_term}')

            print(f"Found {len(movies)} movies with search term '{search_term}' in title.")
            for movie in movies:
                print("{} -- {}".format(movie.Year, movie.Title))
                poster_url = movie.Poster
                try:
                    r = requests.get(poster_url, stream=True)
                    with open(os.path.join(path, f'{search_term}', f'{movie.Title}.jpg'), 'wb') as f:
                        r.raw.deconde_content = True
                        shutil.copyfileobj(r.raw, f)
                except:
                    pass

        except requests.exceptions.ConnectionError:
            print("Error: Can't reach host. Please check your network connection is working properly\n")
        except ValueError as e:
            print("Search text can not be left empty")
            print(e)

    print("Exiting...")


def main():
    print_header()
    search_movie_loop()


if __name__ == '__main__':
    main()


