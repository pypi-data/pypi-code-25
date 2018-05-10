from bomojo.backends import get_movie_backend


def render_movie(movie, backend=None):
    backend = backend or get_movie_backend()

    return {
        'title': movie.title,
        'movie_id': backend.format_external_id(movie.external_id)
    }
