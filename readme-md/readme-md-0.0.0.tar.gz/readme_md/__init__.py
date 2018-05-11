#!/usr/bin/env python
from public import public


@public
def header(title, lvl=3):
    if not lvl:
        lvl = "3"
    number = "#" * lvl
    return "%s %s" % (number, title.rstrip().title())


@public
def image(url, title="", alt=""):
    if not alt:
        alt = ""
    if not title:
        title = ""
    kwargs = dict(url=url, title=title, alt=alt)
    return '![{alt}]({url} "{url}")'.format(**kwargs)


@public
def code(code, language=""):
    if not language:
        language = ""
    kwargs = dict(code=code.lstrip().rstrip(), language=language)
    return """```{language}
{code}
```""".format(**kwargs)


@public
def link():
    raise NotImplementedError  # todo


@public
def lists(items, ordered=False):
    raise NotImplementedError  # todo


@public
def blockquote(text):
    raise NotImplementedError  # todo
