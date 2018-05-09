import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

class ThemePlugin(plugins.SingletonPlugin,toolkit.DefaultDatasetForm):

    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)

    def modify_package_schema(self,schema):

        schema['resources'].update({'uname':[toolkit.get_validator('not_empty')]})

        return schema

    def create_package_schema(self):

        schema = super(ThemePlugin,self).create_package_schema()
        schema = self.modify_package_schema(schema)

        return schema

    def update_package_schema(self):

        schema = super(ThemePlugin,self).update_package_schema()
        schema = self.modify_package_schema(schema)

        return schema

    def show_package_schema(self):

        schema = super(ThemePlugin,self).show_package_schema()
        schema['resources'].update({'uname':[toolkit.get_validator('not_empty')]})

        return schema

    def update_config(self,config_):

        toolkit.add_template_directory(config_,'templates')
        toolkit.add_public_directory(config_, 'public')

    def is_fallback(self):
        return True

    def package_types(self):
        return []
