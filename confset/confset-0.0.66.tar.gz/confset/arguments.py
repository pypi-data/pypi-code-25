from __future__ import print_function
import re
import sys
import confset
import optparse


def create_arg_parser():
    parser = optparse.OptionParser(usage='confset [setting]|[setting=value]')
    parser.add_option('--info', default=False, action='store_true', help='Print help information for options')
    return parser


class ConfsetArguments(object):

    def __init__(self, args=None, options=None):
        """
        Initial method for ConfsetArgument which will be called by bin/confset
        :param args: (list) List of arguments
        :param options: (object) argument option object
        """
        self.args = self.parse_arguments(args)
        self.arg_options = options
        self.name = self.args['namespace']
        self.attr = self.args['attribute']
        self.value = self.args['value']
        self.confset = self.__get_confset()

    def __get_confset(self):
        """
        A private method for getting the correct confset object based on the passed arguments.

        If self.name and self.attr (e.g: `confset name.attr`):
            return confset.ConfigSettings('name.attr')

        else if only has self.name (e.g: `confset name`):
            return confset.ConfigSettings('name')

        else (e.g: `confset`):
            return confset

        :return: (object) confset object
        """
        res = confset if self.name is None else confset.ConfigSettings(self.name)
        return res

    def parse_arguments(self, args=None):
        """
        Parse the confset arguments which provided by user and verify it

        **Valid arguments**
            ```
            $ confset
            $ confset name
            $ confset name.attr
            $ confset name.attr=value
            $ confset name.attr="value with space"
            $ confset name.attr=value_without_space
            ```

        **Invalid arguments**
            ```
            $ confset .name
            $ confset name=value
            $ confset name = value
            $ confset =value
            $ confset name.attr=value with space
            $ confset name.attr=value name.attr1=value
            $ confset name.attr=value; name.attr1=value
            ```

        :param args: (list) List of arguments
        :return: (dict) Parsed argument with dictionary type, e.g:
            ```
            {
                'namespace': <str | None>,
                'attribute': <str | None>,
                'value': <str | None>,
            }
            ```
        """
        args = ' '.join(args).strip()
        rgx_p = r'^(?P<namespace>[a-zA-Z0-9\-\_]+)(\.(?P<attribute>[a-zA-Z0-9\-\_]+))?(=(?P<value>.*))?$'
        rgx_m = re.match(rgx_p, args)
        res = rgx_m.groupdict() if rgx_m else {'namespace': None, 'attribute': None, 'value': None}
        if (args and not rgx_m) or not self.verify_arguments(res):
            print(
                'Incorrect command. The proper confset command should be:',
                '  $ confset name.attr=value',
                sep='\n'
            )
            sys.exit(1)
        return res

    @staticmethod
    def verify_arguments(data):
        """
        Verify arguments. Here is the verified logic:
        
            | verified | namespace | attribute | value |
            |----------|-----------|-----------|-------|
            |   True   |     Y     |     Y     |   Y   |
            |   True   |     Y     |     Y     |   -   |
            |   True   |     Y     |     -     |   -   |
            |   True   |     -     |     -     |   -   |
            |   False  |     -     |     Y     |   -   |
            |   False  |     -     |     -     |   Y   |
            |   False  |     -     |     Y     |   Y   |
            |   False  |     Y     |     -     |   Y   |
            
        :param data: (dict) Parsed arguments, e.g:
            {
                'namespace': 'user',
                'attribute': 'Name,
                'value': 'Eva'
            }
        :return: (bool) Arguments verified result
        """
        if data['value']:
            if not data['namespace'] or not data['attribute']:
                return False
        else:
            if not data['namespace'] and data['attribute']:
                return False
        return True

    def get_filters(self):
        """
        Get conf filter based on the conf name and attribute
        :return: (str)

            if user provides conf name and attribute:
                filter = 'name.attribute'
            else:
                filter = ''
        """
        res = '%s.%s' % (self.name, self.attr) if self.name and self.attr else ''
        return res

    def execute(self):
        """
        Execute the actual confset command based on the args.
        :return: N/A
        """
        if self.name and self.attr and self.value is not None:
            self.confset.set(self.attr, self.value)

        self.confset.print_settings(
            setting_filter=self.get_filters(),
            info=self.arg_options.info
        )
