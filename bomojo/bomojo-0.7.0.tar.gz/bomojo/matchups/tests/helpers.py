from bomojo.movies.models import Movie


def create_movie(title, **kwargs):
    movie_data = {
        'title': title,
        'external_id': title.lower()
    }

    movie_data.update(kwargs)

    return Movie.objects.create(**movie_data)
