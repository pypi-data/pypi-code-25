import urlparse
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from molo.globalsite.models import CountrySite, Region


class CountryView(TemplateView):
    template_name = 'globalsite/country_site.html'

    def get_context_data(self, *args, **kwargs):
        regions = Region.objects.all()
        context = super(CountryView, self).get_context_data(*args, **kwargs)
        context.update({'regions': regions})
        return context


def set_country(request, country_code):
    country = get_object_or_404(CountrySite, code=country_code)
    request.session['GLOBALSITE_COUNTRY_SELECTION'] = country.site_url
    return redirect(country.site_url)


def change_country(request):
    if hasattr(settings, 'GLOBAL_SITE_URL'):
        global_site = settings.GLOBAL_SITE_URL
        url = urlparse.urljoin(global_site, '/globalsite/countries/')
        return redirect(url)
