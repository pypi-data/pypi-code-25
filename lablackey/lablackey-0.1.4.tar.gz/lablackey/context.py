from django.conf import settings

from loader import load_class

PUBLIC_SETTINGS = { s: getattr(settings,s,None) for s in getattr(settings,"PUBLIC_SETTINGS",[]) }

def public_settings(request):
  return {
    'settings': settings,
  }

DEFAULT_META = {}

def meta(request):
  META = getattr(settings,'META',None) or DEFAULT_META
  META = META.copy()
  for lookup in getattr(settings,'META_LOOKUPS'):
    for k,v in (load_class(lookup)(request) or {}).items():
      META[k] = v or META[k]
  return {'META': META}
