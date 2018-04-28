try:
    import cjson as json
except ImportError:
    import json
import os
import re

_COMMENTS_REGEX = re.compile(r'/\*.*?\*/', re.DOTALL)
_INCLUDE_DIRECTIVE = re.compile(
    r'\/\*\#INCLUDE(.*?)\*/|\/\*\ \#INCLUDE(.*?)\*/|\/\/\#INCLUDE(.*\ ?)|\/\/\ \#INCLUDE(.*\ ?)',
    re.IGNORECASE | re.MULTILINE)


def loads(json_file_path, encoding=None, cls=None, object_hook=None, parse_float=None,
          parse_int=None, parse_constant=None, object_pairs_hook=None, error_on_include_file_not_found=False, **kw):
    file_full_path = os.path.abspath(json_file_path)
    file_path = os.path.dirname(file_full_path)
    """Deserializes JSON on the specified file into a dictionary."""
    json_source = ""
    with open(file_full_path, encoding=encoding) as f:
        json_source = _include_files(file_path, f.read(), encoding, error_on_include_file_not_found)
        json_source = _remove_comments(json_source)
    return json.loads(json_source, encoding=encoding, cls=cls, object_hook=object_hook, parse_float=parse_float,
                      parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)


def dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True,
          allow_nan=True, cls=None, indent=None, separators=None,
          default=None, sort_keys=False, **kw):
    """Serializes JSON into string."""
    return json.dumps(obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                      allow_nan=allow_nan, cls=cls, indent=indent, separators=separators,
                      default=default, sort_keys=sort_keys, **kw)


def _include_files(include_files_path, string, encoding=None, error_on_file_not_found=False):
    """Include all files included in current json string"""
    includes = re.finditer(_INCLUDE_DIRECTIVE, string)
    for match_num, match in enumerate(includes):
        included_source = ""
        include_call_string = str(match[match_num])
        file_name = match.groups()[1]
        if file_name is not None:
            file_name = file_name.replace("<", "").replace(">", "").replace("\"", "").replace("'", "").strip(" ")
        include_file_path = os.path.join(include_files_path, file_name)
        if os.path.abspath(include_file_path):
            with open(include_file_path, "r", encoding=encoding) as f:
                included_source = f.read()
                included_source = _remove_comments(included_source).strip(' ').strip('\n').strip('\t')
                # Add Trailing Comma for object separation
                if string.split(include_call_string)[1].strip('\n').strip('\t').strip(' ').startswith(
                        "{") and not included_source.endswith(","):
                    included_source = included_source + ","
                string = string.replace(include_call_string, included_source)

        else:
            if error_on_file_not_found:
                raise IOError("{0} included file was not found.".format(include_file_path))
    return string


def _remove_comments(string):
    """Removes all comments"""
    string = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", string)
    string = re.sub(re.compile("//.*?\n"), "", string)
    return string
