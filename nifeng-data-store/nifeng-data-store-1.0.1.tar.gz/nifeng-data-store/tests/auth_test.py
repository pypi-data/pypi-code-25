# content of test_class.py
from unittest import mock

from app.auth import auth
from app.foundation.constants import constant
from app.users import users_repository
from app.users.user_model import UserModel


def test_should_return_if_identification_is_empty():
    is_success, token, description = auth.authenticate(None, 'password')
    assert is_success is False
    assert description is constant.IDENTIFICATION_IS_REQUIRED


def test_should_return_if_password_is_empty():
    is_success, token, description = auth.authenticate('identification', None)
    assert is_success is False
    assert description is constant.PASSWORD_IS_REQUIRED


@mock.patch.object(users_repository, 'get_user_by_identification')
@mock.patch.object(auth, 'decrypt_password')
@mock.patch.object(auth, 'create_access_token')
def test_should_return_token_if_authenticate_successfully(create_access_token, decrypt_password,
                                                          get_user_by_identification):
    user_model = UserModel()
    user_model.client_no = 'client_no-foo'

    get_user_by_identification.return_value = user_model
    decrypt_password.return_value = '123456'
    create_access_token.return_value = 'token-foo'

    is_success, token, description = auth.authenticate('17512345678', '123456')

    assert is_success is True
    assert token is 'token-foo'


@mock.patch.object(users_repository, 'get_user_by_identification')
def test_should_return_if_user_does_not_exist(get_user_by_identification):
    get_user_by_identification.return_value = None

    is_success, token, description = auth.authenticate('15712345678', '123456')

    assert is_success is False
    assert description is constant.USER_DOES_NOT_EXIST


@mock.patch.object(auth, 'decrypt_password')
@mock.patch.object(users_repository, 'get_user_by_identification')
def test_should_return_if_identification_or_password_is_incorrect(get_user_by_identification, decrypt_password):
    user_model = UserModel()
    user_model.client_no = 'client_no-foo'

    get_user_by_identification.return_value = user_model
    decrypt_password.return_value = '123456'

    is_success, token, description = auth.authenticate('15712345678', '234567')
    assert is_success is False
    assert description is constant.USER_OR_PASSWORD_DOES_NOT_CORRECT


@mock.patch.object(users_repository, 'get_user_by_identification')
@mock.patch.object(auth, 'decrypt_password')
@mock.patch.object(auth, 'safe_str_cmp')
def test_should_return_password_is_incorrect(safe_str_cmp, decrypt_password, get_user_by_identification):
    user_model = UserModel()
    user_model.client_no = 'client_no-foo'

    get_user_by_identification.return_value = user_model
    decrypt_password.return_value = '123456'
    safe_str_cmp.return_value = False

    is_success, token, description = auth.authenticate('15712345678', '234567')
    assert is_success is False
    assert description is constant.USER_OR_PASSWORD_DOES_NOT_CORRECT
