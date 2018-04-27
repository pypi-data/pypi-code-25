# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from fperms.base import BasePerm
from fperms.managers import RelatedPermManager

from fperms_iscore import enums
from fperms_iscore.utils import get_iscore_class
from fperms_iscore.exceptions import IsCoreDoesNotExist


class IsCorePerm(BasePerm):

    PERM_TYPE_CHOICES = enums.PERM_TYPE_CHOICES
    PERM_CODENAMES = enums.PERM_CODENAMES

    core = models.CharField(
        _('core'),
        max_length=100,
    )

    related_manager = RelatedPermManager()

    class Meta:
        base_manager_name = 'related_manager'
        unique_together = (
            ('type', 'codename', 'content_type', 'object_id', 'field_name', 'core'),
        )

    @property
    def _core_perm_name(self):
        return _('core %s') % (
            self.core,
        )

    @property
    def _core_perm_str_args(self):
        return [
            self.type,
            self.core,
            self.codename,
        ]

    @classmethod
    def get_perm_kwargs(cls, perm, obj=None):
        perm_type, perm_arg_string = perm.split('.', 1)

        if perm_type == enums.PERM_TYPE_CORE:
            core, codename = perm_arg_string.rsplit('.', 1)

            try:
                get_iscore_class(core)
            except AttributeError:
                raise IsCoreDoesNotExist(_('provided IsCore does not exist'))

            return dict(
                type=perm_type,
                codename=codename,
                core=core
            )

        return super().get_perm_kwargs(perm=perm, obj=obj)
