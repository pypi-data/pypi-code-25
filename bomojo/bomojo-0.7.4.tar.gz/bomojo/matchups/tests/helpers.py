from bomojo.backends import get_movie_backend
from bomojo.matchups.models import Matchup
from bomojo.movies.models import Movie


def create_movie(title, **kwargs):
    backend = kwargs.pop('backend', None) or get_movie_backend()

    movie_data = {
        'title': title,
        'external_id': backend.parse_movie_id(title.lower())
    }

    movie_data.update(kwargs)

    return Movie.objects.create(**movie_data)


def create_matchup(user, movies, **kwargs):
    backend = kwargs.pop('backend', None) or get_movie_backend()

    matchup_data = {
        'user': user,
        'title': ' vs '.join(movies),
        'description': 'matchup between %s' % ' and '.join(movies),
        'movies': [backend.parse_movie_id(movie_id)
                   for movie_id in movies],
        'period': '30d'
    }

    matchup_data.update(kwargs)

    return Matchup.objects.create(**matchup_data)
