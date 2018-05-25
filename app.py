import tornado
from tornado.escape import json_decode
import tornado.web
import tornado.options
import os
import json
from tornado.httpclient import AsyncHTTPClient, HTTPRequest


class CallbackHandler(tornado.web.RequestHandler):
    async def post(self):

        authorization = self.request.headers.get('Authorization')
        print('\033[94mCallback called with authorization', authorization)

        self.set_status(201)
        self.finish()


class GerarCertidaoHandler(tornado.web.RequestHandler):

    async def post(self):

        data = json_decode(self.request.body)

        wait = self.get_argument('wait', 'true')

        if wait == 'true':
            self.set_status(201)
            self.finish(data)
        else:
            callback_url = self.get_argument('callbackUrl', '')
            callback_user = self.get_argument('callbackUser', '')
            callback_password = self.get_argument('callbackPassword', '')

            import time
            time.sleep(2)

            client = AsyncHTTPClient()

            request = HTTPRequest(
                callback_url,
                method='POST',
                auth_mode='basic',
                auth_username=callback_user,
                auth_password=callback_password,
                body=json.dumps(data),
                validate_cert=False,
            )

            print('callback_url', callback_url)

            def callback(response):
                print('retorno', response)

            response = client.fetch(request, raise_error=True, callback=callback)
            print(response)
            self.set_status(201)
            self.finish({})


class Application(tornado.web.Application):
    def __init__(self):

        handlers = [
            (r"/gerar-certidao", GerarCertidaoHandler),
            (r"/callback", CallbackHandler)
        ]

        settings = {
            "debug": True,
            "autoreload": True
        }

        tornado.web.Application.__init__(
            self, handlers, **settings
        )


app = tornado.httpserver.HTTPServer(Application())

if __name__ == "__main__":
    try:
        tornado.options.parse_command_line()

        app.listen(9999)

        print("Tornado on port: %i" % 9999)

        io_loop = tornado.ioloop.IOLoop.instance()
        io_loop.start()
    except KeyboardInterrupt:
        exit()


'''
How to use

http://localhost:9999/gerar-certidao?wait=0&callbackUrl=http://0.0.0.0:9999/callback&callbackUser=johnicallbackPassword=1234
'''
