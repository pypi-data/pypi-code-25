from django.contrib import admin
from django import forms
from personas.models import CpacRssFeeds, PersonaPublicationJunction, Personas, FeederProcessedArticlesUrls, FeederJobs
from newtable.models import Account, Hub, PersonasToHubs

# Register your models here.
class ChoiceInline(admin.StackedInline):
    model = PersonaPublicationJunction
    extra = 1

class CpacRssFeedsAdmin(admin.ModelAdmin):
    list_display = ('id','url','publication','active')
class PersonasAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active', 'inclusion_terms', 'exclusion_terms')
    inlines = [ChoiceInline]
class PersonasToHubsAdmin(admin.ModelAdmin):
    list_display = ('id','personas','hub')

admin.site.register(CpacRssFeeds,CpacRssFeedsAdmin)
admin.site.register(PersonaPublicationJunction)
admin.site.register(Personas, PersonasAdmin)
admin.site.register(FeederProcessedArticlesUrls)
admin.site.register(FeederJobs)
admin.site.register(Account)
admin.site.register(Hub)
admin.site.register(PersonasToHubs,PersonasToHubsAdmin)