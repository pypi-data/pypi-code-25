from django.utils.deprecation import MiddlewareMixin
from django.http.response import HttpResponse

from .utils import get_page_by_path

import logging

logger = logging.getLogger(__name__)


class DeepPageTemplateRendererMiddleware(MiddlewareMixin):
    '''
        The goal of this middleware is find the respective page by URL, render
        the page content and return it.
    '''

    def process_request(self, request):
        '''
            Look for Deep Page's PATH pattern and return a rendered template
        '''

        # DeepPages must work ONLY if actual response has status_code == 404
        # (Not found). Otherwise, there is no reason to interfere into normal
        # page response behavior.
        if self.get_response(request).status_code == 404:
            rendered_page = get_page_by_path(self, request, logger)

            if rendered_page:
                return HttpResponse(rendered_page)
