"""
Default Django settings
"""

# Movie search
MOVIE_MAX_SEARCH_RESULTS = 20

# Avatars
DEFAULT_AVATAR_SIZE = 32
DEFAULT_AVATAR_STYLE = 'retro'

# Backend containing business logic for exposing functionality to users
USER_BACKEND = 'bomojo.backends.DefaultUserBackend'

# Backend containing business logic related to rendering of movies
MOVIE_BACKEND = 'bomojo.backends.DefaultMovieBackend'
