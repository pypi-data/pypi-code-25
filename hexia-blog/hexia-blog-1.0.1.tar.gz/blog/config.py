from django.apps import AppConfig


class BlogConfig(AppConfig):
    # Full Python path to the application eg. 'django.contrib.admin'.
    name = 'blog'
    # Last component of the Python path to the application eg. 'admin'.
    label = 'blog'
    # Human-readable name for the application eg. "Admin".
    verbose_name = 'Blog'