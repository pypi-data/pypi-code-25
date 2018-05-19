from nhs_dos import users


def test_user_attributes_are_set_correctly():
    username = 'test-username'
    password = 'test-password'
    u = users.User(username, password)
    assert type(u) == users.User
    assert u.username == username
    assert u.password == password


def test_user_string_representations_are_correct():
    username = 'test-username'
    password = 'test-password'
    u = users.User(username, password)
    assert str(u) == "<User test-username>"
    assert u.__repr__() == "<User test-username>"
