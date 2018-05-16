from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import FilePreference


dravatar = Section('dravatar')


@global_preferences_registry.register
class OverlayImage(FilePreference):
    section = dravatar
    name = 'overlay_image'
    default = None
