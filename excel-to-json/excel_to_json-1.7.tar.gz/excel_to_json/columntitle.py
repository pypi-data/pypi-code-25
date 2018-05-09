from enum import Enum
from collections import namedtuple


class Decorator(Enum):
    Empty = 1
    Anchor = 2
    Join = 3
    Ignore = 4


def parse_decorator(title):
    if title.find('#anchor') != -1:
        decorator = Decorator.Anchor
    elif title.find('#join') != -1:
        decorator = Decorator.Join
    elif title == '#ignore':
        decorator = Decorator.Ignore
    else:
        decorator = Decorator.Empty
    return decorator


def title_without_decorator(title):
    decorator_index = title.find('#')
    return title[:] if decorator_index == -1 else title[:decorator_index]


def join_target_sheet(title):
    sheet_separator_index = title.find('/')
    if sheet_separator_index != -1:
        return title[:sheet_separator_index]
    return None


def join_target_column(title):
    begin_index = 0
    sheet_separator_index = title.find('/')
    if sheet_separator_index != -1:
        begin_index = sheet_separator_index + 1
    end_index = title.find('#')
    return title_without_decorator(title[begin_index:] if end_index == -1 else title[begin_index:end_index])


class Type(Enum):
    Attri = 1,
    Array = 2,
    Object = 3,


Component = namedtuple('Component', ['type', 'name'])


def parse_components(title):
    components = []
    decorator_index = title.find('#')
    title_without_decorator = title if decorator_index == -1 else title[:decorator_index]
    raw_components = title_without_decorator.split('.')
    if len(raw_components) > 0:
        for raw_component in raw_components[:-1]:
            components.append(Component(Type.Object, raw_component))
        last_raw_component = raw_components[-1]
        if last_raw_component.endswith('@'):
            components.append(Component(Type.Array, last_raw_component[:-1]))
        else:
            components.append(Component(Type.Attri, last_raw_component))
    return components


def is_valid(title):
    return title is not None and title.strip() != "" and \
           (title.find('#') == -1 or parse_decorator(title)!=Decorator.Empty)
