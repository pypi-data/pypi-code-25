import tornado.ioloop
import tornado.web
import json


class PiggyFly(object):
    def __init__(self, prediction):

        class ProcessHandler(tornado.web.RequestHandler):
            def post(self):
                body = json.loads(self.request.body)
                data = body['param']
                self.finish({'result': prediction(data)})

        self.app = tornado.web.Application([
            (r"/", ProcessHandler),
        ])

    def serv(self, port=8080):
        self.app.listen(port)
        tornado.ioloop.IOLoop.current().start()