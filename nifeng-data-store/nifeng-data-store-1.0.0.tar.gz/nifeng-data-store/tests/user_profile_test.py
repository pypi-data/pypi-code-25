from unittest import mock

from app.users import users_repository
from app.users import users_service
from app.users.user_model import UserModel


@mock.patch.object(users_repository, 'get_profile')
def test_should_return_user_profile(get_profile):
    given_client_no = 'client-no-foo'

    user_model = UserModel()
    user_model.client_no = 'client-no-foo'
    user_model.name = 'foo-name'
    user_model.email = 'name@example.com'
    user_model.mobile = '15800000000'

    get_profile.return_value = user_model

    is_success, user_profile_result, description = users_service.get_profile(given_client_no)

    assert is_success is True
    assert user_profile_result.client_no is 'client-no-foo'
    assert user_profile_result.name is 'foo-name'
    assert user_profile_result.mobile is '15800000000'
    assert user_profile_result.email is 'name@example.com'


@mock.patch.object(users_repository, 'get_profile')
def test_should_return_none_if_no_user_profile_was_found(get_profile):
    given_client_no = 'client-no-foo'
    get_profile.return_value = None

    is_success, user_profile_result, description = users_service.get_profile(given_client_no)

    assert is_success is False
    assert user_profile_result is None
