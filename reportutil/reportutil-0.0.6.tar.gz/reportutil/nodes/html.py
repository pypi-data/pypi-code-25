# encoding: utf-8

import logging_helper
from dominate import tags
from fdutil.html import (write_to_html,
                         generate_html_document,
                         CSS_DIV_ID)
from reportutil.components.file import ReportFileNode

logging = logging_helper.setup_logging()


class HTMLReport(ReportFileNode):

    ADD_METHOD = u'html'

    def generate(self):

        if len(self._report_objects) > 0:
            doc = generate_html_document(title=self.name)

            with doc:
                for obj in self._report_objects:
                    obj.html()

                    # Add any extra CSS from object
                    # TODO: Is this the best method?
                    # TODO: de-dupe css from multiple of the same object?
                    css = getattr(obj, u'CSS', False)
                    inline_css = getattr(obj, u'INLINE_CSS', False)

                    if css or inline_css:
                        css_div = doc.getElementById(CSS_DIV_ID)

                        if css:
                            for c in css:
                                css_div.add(tags.style(c))

                        if inline_css:
                            for c in inline_css:
                                css_div.add(tags.style(c))

            write_to_html(html_document=doc,
                          filename=self.filename,
                          html_folder=self.parent.path)
