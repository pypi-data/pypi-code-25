import configparser
from .forms import DefaultForm, EmailForm, SiteForm


ASYNC_NUM_DEFAULT = 10


class Config:
    default = {}
    email = {}
    sites = []
    default_required_options = ['type', 'urls', 'sitemap']
    email_required_options = ['smtp_server', 'port', 'user', 'password', 'sender', 'receiver']
    is_critical_error = False
    is_email_error = False
    errors = {}

    @classmethod
    def parse_config(cls, conf_path):
        config = configparser.ConfigParser()
        config.read(conf_path)
        for section in config.sections():
            opts = {}
            for option in config.options(section):
                opts[option] = config.get(section, option)
            opts['name'] = section
            if section.lower() == 'default':
                cls.default = opts
            elif section.lower() == 'email':
                cls.email = opts
            else:
                cls.sites.append(opts)
        cls._validate()

    @classmethod
    def get_errors(cls):
        text = 'Find next errors in config file:\n'
        for section_name, errors in cls.errors.items():
            text += '\t%s:\n' % section_name
            for field_name, error in errors.items():
                text += '\t\t%s - %s\n' % (field_name, ', '.join(error))
        return text

    @classmethod
    def _validate(cls):
        cls._validate_default_options()
        cls._validate_sites_options()
        cls._validate_email_options()

    @classmethod
    def _validate_sites_options(cls):
        sites_without_url = 0
        for i, site in enumerate(cls.sites):
            form = SiteForm(site)
            if not form.is_valid:
                cls.errors['site_'+str(i)] = form.get_errors()
                sites_without_url += 1

        if sites_without_url == len(cls.sites):
            cls.is_critical_error = True

    @classmethod
    def _validate_default_options(cls):
        form = DefaultForm(cls.default)
        if not form.is_valid:
            cls.errors['default'] = form.get_errors()
            cls.is_critical_error = True
        cls.default['async_num'] = int(cls.default.get('async_num', ASYNC_NUM_DEFAULT))

    @classmethod
    def _validate_email_options(cls):
        form = EmailForm(cls.email)
        if not form.is_valid:
            cls.errors['email'] = form.get_errors()
            cls.is_email_error = True

    @classmethod
    def get_urls_with_sitemap(cls):
        return [site for site in cls.sites if site.get('type', cls.default['type']) == 'sitemap']

    @classmethod
    def get_urls_without_sitemap(cls):
        return [site for site in cls.sites if site.get('type', cls.default['type']) == 'urls']
