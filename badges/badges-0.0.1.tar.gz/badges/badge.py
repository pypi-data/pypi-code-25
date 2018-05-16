#!/usr/bin/env python
from public import public


# format string:
# "a={a}, b={b}, c={c}".format(**vars(obj)) # variables only
# 'a={0.a}, b={0.b}, c={0.c}'.format(obj)


@public
class Badge:
    image = None
    link = ""
    title = ""
    markup = "md"
    branch = "master"

    def __init__(self, **kwargs):
        self.update(**kwargs)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def format_string(self, string):
        kwargs = dict()
        kwargs.update(**vars(self))
        kwargs.update(**vars(self.__class__))
        return string.format(self, **kwargs)

    def get_image(self):
        if not self.image:
            raise ValueError("image EMPTY")
        return self.format_string(self.image)

    def get_link(self):
        return self.format_string(self.link or "")

    def get_title(self):
        return self.format_string(self.title or "")

    def render_md(self):
        return "[![%s](%s)](%s)" % (self.get_title(), self.get_image(), self.get_link())

    def render_rst(self):
        target = self.link
        if not self.link:
            target = "none"
        return """.. image: : %s
    : target: %s""" % (self.get_image(), target)

    def render(self, markup):
        if markup == "md":
            return self.render_md()
        if markup == "rst":
            return self.render_rst()
        raise ValueError("'%s' unknown markup" % markup)

    @property
    def visible(self):
        return True

    def __bool__(self):
        return self.visible

    def __nonzero__(self):
        return self.visible

    def __str__(self):
        if self:
            return self.render(self.markup)
        return ""

    def __repr__(self):
        return self.__str__()
