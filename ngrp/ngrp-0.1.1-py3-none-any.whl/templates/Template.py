from abc import ABC
import string


class Template(ABC):
    """Nginx configuration file template.
    Template should be given as docstring with parameters
    enclosed in <pointy> brackets.
    """

    __ESCAPE_TABLE = str.maketrans({
            "<": "{",
            ">": "}",
            "{": "<",
            "}": ">",
        })
    __formatter = string.Formatter()

    def __init__(self):
        self.parameters = Template.__extract_parameters(self.__doc__)
        self._template_str = self.__doc__.translate(Template.__ESCAPE_TABLE)

    def format(self, **kwargs):
        """Returns template formatted with requrired arguments.
        Argument list is extracted from the template string
        (arguments are enclosed in <pointy> brackets).
        """

        missing_keys = [param for param in self.parameters
                        if param not in kwargs]
        if missing_keys:
            class_name = self.__class__.__name__
            raise TypeError("{}.format() requires {}. Missing parameters: {}.".format(
                class_name, ", ".join(self.parameters), ", ".join(missing_keys)))

        filled_template = self._template_str.format_map(kwargs)
        return filled_template.translate(Template.__ESCAPE_TABLE)

    @staticmethod
    def __extract_parameters(template_str):
        template_str = template_str.translate(Template.__ESCAPE_TABLE)
        parsed_docstring = Template.__formatter.parse(template_str)
        parameters = [parameter
                      for (_, parameter, _, _) in parsed_docstring
                      if parameter]
        return parameters
