from typing import Dict


class Option:
    def __init__(self, original_name, name, short_name, default, type, description):
        self.original_name = original_name
        self.name = name
        self.short_name = short_name
        self.default = default
        self.type = type
        self.description = description


class Argument:
    def __init__(self, name, type, description):
        self.name = name
        self.type = type
        self.description = description


class Interface:
    def __init__(self, name: str, description: str, arguments: Dict[str, Argument], options: Dict[str, Option]):
        self.name = name
        self.description = description
        self.arguments = arguments
        self.options = options
