"""
Application views/routes are based on Flask's MethodView. All primary views are
combined into a Flask blueprint.
"""
__author__ = 'Ralph Seichter'

import json
from operator import attrgetter
from urllib.parse import urlparse, urljoin
from uuid import uuid4

from flask import Blueprint, flash, request, redirect, abort, url_for
from flask.templating import render_template
from flask.views import MethodView, View
import flask_login
from flask_login.utils import current_user

from .esi import IdNameCache
from .extensions import db, login_manager, pwd_context
from .forms import LoginForm, SignupForm
from .models import User, character_list_loader, user_loader
from .sso import EveSso
import swagger_client
from swagger_client.rest import ApiException

eveCache = IdNameCache()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


class RenderTemplate(View):

    def __init__(self, template):
        self.template = template

    def dispatch_request(self):
        return render_template(self.template)


class Signup(MethodView):
    methods = ['GET', 'POST']

    def get(self):
        return render_template('signup.html', form=SignupForm())

    def post(self):
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        if not (email and password and confirm):
            flash('Please fill all fields.', 'warning')
            return render_template('signup.html', form=SignupForm())

        if password != confirm:
            flash('Passwords do not match.', 'warning')
            return redirect(url_for('.signup'))

        if user_loader(email):
            flash('This address is already registered.', 'warning')
            return redirect(url_for('.signup'))

        user = User(email, password, str(uuid4()))
        db.session.add(user)
        db.session.commit()
        flash('Registration successful, you may now login.', 'success')
        return redirect(url_for('.index'))


class Login(MethodView):
    methods = ['GET', 'POST']

    def get(self):
        return render_template('login.html', form=LoginForm())

    def post(self):
        user = request_loader(request)
        if user:
            flask_login.login_user(user)
            target = request.args.get('next')
            if not is_safe_url(target):
                return abort(400)
            return redirect(target or url_for('.dashboard'))
        flash('Your login was not successful.', 'danger')
        return redirect(url_for('.login'))


class Logout(MethodView):
    methods = ['GET']

    def get(self):
        flask_login.logout_user()
        flash('You are logged out.', 'success')
        return redirect(url_for('.index'))


class Dashboard(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self):
        characters = character_list_loader(flask_login.current_user.uuid)
        auth_url, auth_state = EveSso().auth_url_state()
        return render_template(
            'dashboard.html',
            characters=sorted(characters, key=attrgetter('name')),
            auth_url=auth_url,
            auth_state=auth_state
        )


class Character(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self, character_id):
        api = swagger_client.CharacterApi()
        try:
            rv = api.get_characters_character_id(character_id)
        except ApiException as e:
            return api_fail(e)
        return render_template('character.html', character=rv)


def refresh_token(api, cc):
    es = EveSso(json.loads(cc.token_str))
    token_dict, is_new_token = es.refresh_token()
    if is_new_token:  # pragma: no cover (Can't test without valid tokens)
        cc.set_token(token_dict)
        db.session.merge(cc)
        db.session.commit()
    client = api.api_client
    client.set_default_header('User-Agent', 'BootiniStar/0.0.1')
    client.configuration.access_token = token_dict['access_token']
    return token_dict


def api_fail(api_exception):
    flash('EVE Swagger Interface call failed: ' +
          api_exception.reason + '.', 'danger')
    return redirect(url_for('.index'))


class MailList(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self, character_id):
        cc = current_user.load_character(character_id)
        if cc:  # pragma: no cover (Never true without valid tokens in DB)
            api = swagger_client.MailApi()
            refresh_token(api, cc)
            try:
                rv = api.get_characters_character_id_mail(character_id)
                return render_template('maillist.html', eveCache=eveCache,
                                       character_id=character_id, maillist=sorted(rv, key=attrgetter('timestamp'), reverse=True))
            except ApiException as e:
                return api_fail(e)
        else:
            flash('Please select one of your characters.', 'warning')
        return redirect(url_for('.dashboard'))


class Mail(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self, args):
        x = args.split(',')
        character_id = int(x[0])
        mail_id = int(x[1])
        cc = current_user.load_character(character_id)
        if cc:
            api = swagger_client.MailApi()
            refresh_token(api, cc)
            try:  # pragma: no cover (Needs valid tokens)
                rv = api.get_characters_character_id_mail_mail_id(
                    character_id, mail_id)
                return render_template('mail.html', eveCache=eveCache, mail=rv)
            except ApiException as e:  # pragma: no cover (Needs valid tokens)
                return api_fail(e)
        else:
            flash('Please select one of your characters.', 'warning')
        return redirect(url_for('.dashboard'))


class RemoveCharacter(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self, character_id):
        cc = current_user.load_character(character_id)
        if cc:
            db.session.delete(cc)
            db.session.commit()
            flash('Character ' + cc.name + ' was removed.', 'success')
        else:
            flash('Please select one of your characters.', 'warning')
        return redirect(url_for('.dashboard'))


class Skills(MethodView):
    methods = ['GET']

    @flask_login.login_required
    def get(self, character_id):
        cc = current_user.load_character(character_id)
        if cc:  # pragma: no cover (Never true without valid tokens in DB)
            api = swagger_client.SkillsApi()
            refresh_token(api, cc)
            try:
                rv = api.get_characters_character_id_skillqueue(character_id)
                return render_template('skillqueue.html', eveCache=eveCache,
                                       character_id=character_id, skillq=sorted(rv, key=attrgetter('queue_position')))
            except ApiException as e:
                return api_fail(e)
        else:
            flash('Please select one of your characters.', 'warning')
        return redirect(url_for('.dashboard'))


blueprint = Blueprint('bs', __name__)
blueprint.add_url_rule(
    '/', view_func=RenderTemplate.as_view('index', template='index.html'))
blueprint.add_url_rule('/dashboard', view_func=Dashboard.as_view('dashboard'))
blueprint.add_url_rule('/dashboard/rm/<int:character_id>',
                       view_func=RemoveCharacter.as_view('rmcharacter'))
blueprint.add_url_rule('/login', view_func=Login.as_view('login'))
blueprint.add_url_rule('/logout', view_func=Logout.as_view('logout'))
blueprint.add_url_rule('/signup', view_func=Signup.as_view('signup'))
blueprint.add_url_rule('/character/<int:character_id>',
                       view_func=Character.as_view('character'))
blueprint.add_url_rule('/mail/<string:args>', view_func=Mail.as_view('mail'))
blueprint.add_url_rule('/maillist/<int:character_id>',
                       view_func=MailList.as_view('maillist'))
blueprint.add_url_rule('/skillqueue/<int:character_id>',
                       view_func=Skills.as_view('skillqueue'))


@login_manager.request_loader
def request_loader(request):
    user = user_loader(request.form.get('email'))
    if user and request.form['password'] and pwd_context.verify(request.form['password'], user.password):
        return user
    return None
