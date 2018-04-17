from is_core.main import UIRESTModelISCore


from fperms_iscore.mixins import PermIsCoreMixin


class PermUIRESTModelISCore(PermIsCoreMixin, UIRESTModelISCore):

    abstract = True

