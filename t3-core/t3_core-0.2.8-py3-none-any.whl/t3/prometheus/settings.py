"""Base settings for using django-prometheus."""


PROMETHEUS_INSTALLED_APPS = ['django_prometheus', ]

PROMETHEUS_BEFORE_MIDDLEWARE = ['django_prometheus.middleware.PrometheusBeforeMiddleware', ]

PROMETHEUS_AFTER_MIDDLEWARE = ['django_prometheus.middleware.PrometheusAfterMiddleware', ]
