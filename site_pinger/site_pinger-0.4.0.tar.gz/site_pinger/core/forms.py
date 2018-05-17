from .fields import BaseField, CharField, EmailField, IntField, UrlField, XmlUriField, ChoiceField


class BaseForm:
    def __init__(self, conf):
        self.errors = {}
        self.is_valid = True
        for field_name in self.__class__.__dict__.keys():
            field = getattr(self, field_name)
            if isinstance(field, BaseField):
                field.set_value(conf.get(field_name, None))
                field.validate()
                if len(field.errors):
                    self.is_valid = False
                    self.errors[field_name] = field.errors
        print(self.__class__, self.errors)

    def get_errors(self):
        return self.errors


class DefaultForm(BaseForm):
    type = ChoiceField(required=True, choices=['sitemap', 'urls'])
    sitemap = XmlUriField(required=True)
    urls = CharField(required=True)
    async_num = IntField(required=True)


class EmailForm(BaseForm):
    smtp_server = CharField(required=True)
    port = IntField(required=True)
    user = CharField(required=True)
    password = CharField(required=True)
    sender = EmailField(required=True)
    receiver = EmailField(required=True)


class SiteForm(BaseForm):
    url = UrlField(required=True)
    type = ChoiceField(choices=['sitemap', 'urls'])
    sitemap = XmlUriField()
    urls = CharField()
