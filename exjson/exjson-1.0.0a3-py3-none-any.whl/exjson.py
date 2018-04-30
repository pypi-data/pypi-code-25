try:
    import cjson as json
except ImportError:
    import json
import os
import re

_JSON_OPENING_CHARS = [',', '[', '{', ':']
_JSON_CLOSING_CHARS = [',', '}', ']']
_COMMENTS_REGEX = re.compile(r'/\*.*?\*/', re.DOTALL)
_INCLUDE_DIRECTIVE = re.compile(
    r'\/\*\#INCLUDE(.*?)\*/|\/\*\ \#INCLUDE(.*?)\*/|\/\/\#INCLUDE(.*\ ?)|\/\/\ \#INCLUDE(.*\ ?)',
    re.IGNORECASE | re.MULTILINE)


def load(json_file_path, encoding=None, cls=None, object_hook=None, parse_float=None,
         parse_int=None, parse_constant=None, object_pairs_hook=None, error_on_include_file_not_found=False, **kw):
    """Decodes a JSON source file into a dictionary"""
    file_full_path = os.path.abspath(json_file_path)
    file_path = os.path.dirname(file_full_path)
    with open(file_full_path, encoding=encoding) as f:
        json_source = f.read()
    return loads(json_source, encoding=encoding, cls=cls, object_hook=object_hook, parse_float=parse_float,
                 parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=object_pairs_hook,
                 error_on_include_file_not_found=error_on_include_file_not_found, includes_path=file_path, **kw)


def loads(json_string, encoding=None, cls=None, object_hook=None, parse_float=None,
          parse_int=None, parse_constant=None, object_pairs_hook=None,
          error_on_include_file_not_found=False, includes_path=None, **kw):
    """Decodes a provided JSON source string into a dictionary"""
    if json_string is None or json_string.strip(' ') == '':
        raise AttributeError('No JSON source was provided for decoding.')
    if includes_path is None:
        includes_path = os.path.dirname(os.path.realpath(__file__))
    json_source = _include_files(includes_path, json_string, encoding, error_on_include_file_not_found)
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
    # Files Cache
    included_file_cache = {}
    for match_num, match in enumerate(includes):
        if len(match.groups()) > 0:
            for value in match.groups():
                if value is None:
                    continue
                included_source = ""
                include_call_string = str(match.group())
                property_name = ""
                file_name = _remove_enclosing_chars(value)
                if ":" in file_name:
                    values = file_name.split(":")
                    property_name = values[0]
                    file_name = values[1]
                include_file_path = os.path.normpath(os.path.join(include_files_path, file_name))
                if os.path.abspath(include_file_path):
                    # Cache File if not already cached.
                    if include_file_path not in included_file_cache:
                        with open(include_file_path, "r", encoding=encoding) as f:
                            included_file_cache[include_file_path] = f.read()
                    included_source = included_file_cache[include_file_path]
                    # Extract content from include file removing comments, end of lines and tabs
                    included_source = _remove_comments(included_source).strip(' ').strip('\r\n').strip('\n').strip(
                        '\t')
                    # Add Property Name if specified
                    if property_name is not None and property_name.strip(' ') != '':
                        included_source = "\"{0}\": {1}".format(property_name, included_source)
                    # Add Comma if needed and determine if property is required
                    included_source_first_char = _get_first_char(included_source)
                    included_source_last_char = _get_last_char(included_source)
                    included_source_surrounding_src = string.split(include_call_string)
                    included_source_surrounding_src_count = len(included_source_surrounding_src) - 1
                    for i in range(0, included_source_surrounding_src_count):
                        included_call_pre_last_char = _get_last_char(_remove_comments(included_source_surrounding_src[i]))
                        # Add comma at the beginning of the included code if required
                        if included_call_pre_last_char not in _JSON_OPENING_CHARS and included_source_first_char != ',':
                            included_source = "," + included_source
                        # Add Trailing comma if code following the included statement does not have one.
                        if i < included_source_surrounding_src_count:
                            if included_source_last_char != ',' and _get_first_char(
                                    _remove_comments(included_source_surrounding_src[i + 1])) not in _JSON_CLOSING_CHARS:
                                included_source = included_source + ','
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


def _remove_enclosing_chars(string):
    return string.replace("<", "").replace(">", "").replace("\"", "").replace("'", "").strip(" ")


def _get_last_char(string):
    return string.replace(' ', '').replace('\r\n', '').replace('\n', '')[-1:]


def _get_first_char(string):
    return string.replace(' ', '').replace('\r\n', '').replace('\n', '')[:1]
