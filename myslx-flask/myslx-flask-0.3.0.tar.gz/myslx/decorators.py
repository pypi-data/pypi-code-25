from functools import wraps

from myslx import config
from flask import g, url_for, abort
from werkzeug.utils import redirect
from myslx.utils import check_required_roles


def login_required(roles=None):

    def wrapper(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user is None:
                return redirect(
                    f"https://{config.PORTAL_DOMAIN}/auth/oauth/authorize?client_id={config.OAUTH_CLIENT_ID}&response_type=code&redirect_uri={url_for('myslx.callback', _external=True)}"
                )

            if check_required_roles(roles, g.user['authorities']) is False:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return wrapper
