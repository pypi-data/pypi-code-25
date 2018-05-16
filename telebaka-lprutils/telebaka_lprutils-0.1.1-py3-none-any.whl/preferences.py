from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import StringPreference


lprutils = Section('lprutils')


@global_preferences_registry.register
class LinkTemplate(StringPreference):
    section = lprutils
    name = 'notifications_chat_id'
    default = ''
