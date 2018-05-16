from django.contrib import admin

from telebaka_dravatar.models import BotUsage, BotUser


@admin.register(BotUsage)
class BotUsageAdmin(admin.ModelAdmin):
    list_display = 'date', 'usages',


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = 'user_id', 'username', 'name'

