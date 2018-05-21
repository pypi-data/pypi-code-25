import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from bs4 import BeautifulSoup
from yangsutil import WebUtil


class ForTestWebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(bytes("<html><body><h1>GET</h1></body></html>", 'utf-8'))
        return

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        self.wfile.write(post_data)
        return


class WebUtilTestCase(unittest.TestCase):

    # @unittest.skip('web_util test1 skip')
    def test_1_get_post_test(self):
        server = HTTPServer(('', 48080), ForTestWebServer)
        thread = threading.Thread(target=server.serve_forever)
        thread.setDaemon(True)

        if thread.is_alive() is False:
            thread.start()

        get = WebUtil.get(url='http://localhost:48080')
        post = WebUtil.post(url='http://localhost:48080', data_dict={'a': 'b'}, ret_type='json')

        self.assertDictEqual(
            get,
            {
                'status': True,
                'data': "<html><body><h1>GET</h1></body></html>"
            },
            msg='get test'
        )

        self.assertDictEqual(
            post,
            {
                'status': True,
                'data': {
                    'a': 'b'
                }
            },
            msg='post test'
        )

        server.server_close()

    # @unittest.skip('web_util test2 skip')
    def test_2_get_crawl_test(self):
        self.assertEqual(
            type(WebUtil.crawl('http://example.com/', output_type='html')),
            BeautifulSoup,
            msg='html type check'
        )

        self.assertEqual(
            type(WebUtil.crawl('http://example.com/', output_type='text')),
            str,
            msg='str type check'
        )

        self.assertIsNone(
            WebUtil.crawl('http://example.com/', output_type='aaaa'),
            msg='output type error'
        )

        self.assertIsNone(
            WebUtil.crawl('http://exampleaa.com/', output_type='html'),
            msg='invalid address error'
        )
