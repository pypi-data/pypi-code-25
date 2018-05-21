from django.contrib.gis.geoip2 import GeoIP2
from molo.globalsite.models import CountrySite


def get_country_site(request):
    try:
        return CountrySite.objects.get(
            code=get_country_code(request)).site_url
    except CountrySite.DoesNotExist:
        return None


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')


def get_country_code(request):
    try:
        return GeoIP2().country_code(get_client_ip(request))
    except:
        return None
