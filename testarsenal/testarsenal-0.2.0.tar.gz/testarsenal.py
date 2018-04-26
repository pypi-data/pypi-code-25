from time import sleep
from unittest.mock import patch, Mock
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.urls import resolve
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

__version__ = "0.2.0"
__author__ = "Sam Ireland"

class DjangoTest(TestCase):

    def check_url_returns_view(self, url, view):
        resolver = resolve(url)
        self.assertEqual(resolver.func, view)


    def make_request(self, path, method="get", data=None, loggedin=False):
        factory = RequestFactory()
        data = data if data else {}
        if  method == "post":
            request = factory.post(path, data=data)
        else:
            request = factory.get(path, data=data)
        request.user = Mock()
        request.session = {}
        if loggedin:
            request.user.is_authenticated = True
        else:
            request.user.is_authenticated = False
        return request


    def check_view_uses_template(self, view, request, template, *args):
        views = view.__module__
        render_patcher = patch(views + ".render")
        mock_render = render_patcher.start()
        try:
            response = view(request, *args)
            self.assertTrue(mock_render.called)
            self.assertEqual(mock_render.call_args_list[0][0][1], template)
        finally:
            render_patcher.stop()


    def check_view_has_context(self, view, request, context, *args):
        views = view.__module__
        render_patcher = patch(views + ".render")
        mock_render = render_patcher.start()
        try:
            response = view(request, *args)
            self.assertTrue(mock_render.called)
            if len(mock_render.call_args_list[0][0]) <= 2:
                self.fail("No context sent")
            sent_context = mock_render.call_args_list[0][0][2]
            for key in context:
                self.assertEqual(sent_context[key], context[key])
        finally:
            render_patcher.stop()


    def check_view_redirects(self, view, request, url, *args):
        response = view(request, *args)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)


    def check_all_objects_sent(self, model):
        patcher = patch(
         model.__module__ + "." + model.__class__.__name__ + "objects.all"
        )
        mock_all = patcher.start()




class BrowserTest:

    NoElement = NoSuchElementException

    def get(self, path):
        self.browser.get(self.live_server_url + path)


    def check_page(self, url):
        self.assertEqual(self.browser.current_url, self.live_server_url + url)


    def check_title(self, text):
        self.assertIn(text, self.browser.title)


    def check_h1(self, text):
        self.assertIn(text, self.browser.find_element_by_tag_name("h1").text)


    def scroll_to(self, element):
        self.browser.execute_script("arguments[0].scrollIntoView();", element)


    def click(self, element):
        self.scroll_to(element)
        element.click()
        sleep(0.5)


    def sleep(self, duration):
        sleep(duration)


    def check_invisible(self, element):
        self.assertEqual(element.value_of_css_property("display"), "none")


    def check_visible(self, element):
        self.assertNotEqual(element.value_of_css_property("display"), "none")


    def get_select_value(self, dropdown):
        dropdown = Select(dropdown)
        return dropdown.first_selected_option.text


    def get_select_values(self, dropdown):
        return [option.text for option in dropdown.find_elements_by_tag_name("option")]


    def select_dropdown(self, dropdown, option):
        dropdown = Select(dropdown)
        dropdown.select_by_visible_text(option)
