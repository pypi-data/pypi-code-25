import os
import bottle
import warnings
from .db import DB


app = bottle.Bottle()
SECRET = os.environ.get("BOTTLE_APP_SECRET")
if SECRET is None:
    warnings.warn("BOTTLE_APP_SECRET is not set in Environment")
    SECRET = 'This is not secret'
COOKIE_NAME = 'token'


@app.post("/login")
def login():
    uname = bottle.request.json.get('uname')
    pwd = bottle.request.json.get('pwd')
    logged, tok = DB.login_user(uname, pwd)
    if logged:
        bottle.response.set_cookie(COOKIE_NAME, tok, secret=SECRET)
    return 'ok'


@app.route('/logout')
def logout():
    token = bottle.request.get_cookie(COOKIE_NAME, secret=SECRET)
    DB.logout_user(token)
    bottle.response.delete_cookie(COOKIE_NAME, secret=SECRET)
    return ''


@app.route('/<url:re:.*>')
def verify_auth(url):
    token = bottle.request.get_cookie(COOKIE_NAME, secret=SECRET)
    if not DB.is_logged_in(token):
        bottle.abort(403, 'Not authorized')
    url = bottle.request.url
    bottle.response.set_header("X-Accel-Redirect", url)
    return 'ok'


def run_server(host, port):
    app.run(host=host, port=port)
