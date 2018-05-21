from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register, ModelAdminGroup)
from models import CountrySite, Region


class RegionModelAdmin(ModelAdmin):
    model = Region
    menu_label = 'Region'
    menu_icon = 'doc-full'
    add_to_settings_menu = False
    list_display = ['name']


class CountrySiteModelAdmin(ModelAdmin):
    model = CountrySite
    menu_label = 'Country Sites'
    menu_icon = 'doc-full'
    add_to_settings_menu = False
    list_display = ['name', 'site_url']


class GlobalSiteAdminGroup(ModelAdminGroup):
    menu_label = 'Global Site'
    menu_icon = 'folder-open-inverse'
    menu_order = 400
    items = (RegionModelAdmin, CountrySiteModelAdmin)


modeladmin_register(GlobalSiteAdminGroup)
