import glob
import os
import re


class NoMatchingThemeFoundException(Exception):
    pass


THEMES_DIR = os.path.expanduser('~/.mintty/themes')
THEME_PATHS = glob.glob(os.path.join(THEMES_DIR, '*.minttyrc'))

ESCAPE_BEGIN = '\033]'
ESCAPE_END = '\a'

COLORS = dict(
    foregroundcolour='10;',
    backgroundcolour='11;',
    cursorcolour='12;',
    black='4;0;',
    blue='4;4;',
    cyan='4;6;',
    green='4;2;',
    magenta='4;5;',
    red='4;1;',
    white='4;7;',
    yellow='4;3;',
    boldblack='4;8;',
    boldblue='4;12;',
    boldcyan='4;14;',
    boldgreen='4;10;',
    boldmagenta='4;13;',
    boldred='4;9;',
    boldwhite='4;15;',
    boldyellow='4;11;',
)


def get_name(theme_path):
    (theme_name, _) = os.path.splitext(os.path.basename(theme_path))
    return theme_name


def set_color(color_name, value):
    print('{begin}{color_name}{value}{end}'.format(
        begin=ESCAPE_BEGIN,
        color_name=COLORS[color_name.lower()],
        value=value,
        end=ESCAPE_END), end='')


def find_themes():
    return [get_name(tp) for tp in THEME_PATHS]


def select_theme(pattern):
    regex = re.compile(pattern)
    for theme_path in THEME_PATHS:
        theme_name = get_name(theme_path)
        if regex.search(theme_name):
            with open(theme_path) as theme_file:
                for line in theme_file:
                    stripped_line = line.strip()
                    parts = stripped_line.split('=')
                    color_name = parts[0]
                    value = parts[1]
                    set_color(color_name, value)
                return
    raise NoMatchingThemeFoundException()
