from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting
class GlobalSiteSettings(BaseSetting):
    is_globalsite = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=("Activate Global Site"),
        help_text='When activated it will set the'
        ' current site as the global site.'
    )
    autoredirect = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=("Activate Auto Redirect"),
        help_text='When activated it will automatically redirect the'
        ' users to the country of their choice when accessing the global site.'
    )
    geolocation = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=("Activate Geolocation"),
        help_text='When activated it will detect users country and'
        ' redirect them to the supported country site. If the detected country'
        ' is not available it will display the available country sites.'
    )
    description = models.TextField(
        null=True, blank=True,
        help_text='This description will be displayed'
                  ' on the homepage of the global site'
    )
    show_country = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=("Display Country"),
        help_text='When activated, the country name will be displayed'
                  ' and users will be able to change their country site.'
    )
    panels = [
        MultiFieldPanel(
            [
                FieldPanel('is_globalsite'),
                FieldPanel('autoredirect'),
                FieldPanel('geolocation'),
                FieldPanel('description'),
            ],
            heading="Global Site Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_country'),
            ],
            heading="Country Site Settings",
        )
    ]


class Region(models.Model):
    name = models.CharField(max_length=128, verbose_name=("Region"))
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Country Region'

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('name'),
                ImageChooserPanel('image'),
            ],
            heading="country details",
        )
    ]


class CountrySite(models.Model):
    name = models.CharField(max_length=128, verbose_name="Country Name")
    code = models.CharField(
        max_length=6, verbose_name="Country Code",
        help_text='eg. ZA')
    site_url = models.CharField(
        max_length=128,
        help_text='Link to the country site. eg. http://www.zm.sitename.org/')
    region = models.ForeignKey(
        'globalsite.Region', related_name='country_sites',
        verbose_name='Country Region', blank=True, null=True,
        on_delete=models.SET_NULL)
    flag = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    class Meta:
        verbose_name = 'Country site'

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        return super(CountrySite, self).save(*args, **kwargs)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('name'),
                FieldPanel('code'),
                FieldPanel('site_url'),
                FieldPanel('region'),
                ImageChooserPanel('flag'),
            ],
            heading="country details",
        )
    ]
