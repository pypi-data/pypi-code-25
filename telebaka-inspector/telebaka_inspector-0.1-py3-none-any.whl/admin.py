from django.contrib import admin

from telebaka_inspector.models import Message


@admin.register(Message)
class BotUsageAdmin(admin.ModelAdmin):
    list_display = 'id', 'user_id',

