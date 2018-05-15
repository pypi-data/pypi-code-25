import json

from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.forms.jsonb import (
    InvalidJSONInput,
    JSONField as JSONFormField,
)


class UTF8JSONFormField(JSONFormField):

    def prepare_value(self, value):
        if isinstance(value, InvalidJSONInput):
            return value
        return json.dumps(value, ensure_ascii=False)


class UTF8JSONField(JSONField):
    """
    Корректно отображает юникодные символы в админке
    """

    def formfield(self, **kwargs):
        return super().formfield(**{
            **{'form_class': UTF8JSONFormField},
            **kwargs,
        })
