import os
import json

""" create_user opens a json file of user-account data and inserts new user account data into the file, assuming
that the new user isn't already present in the data-file
    """


def create_user(form, jsonpath, authentication_method=None, roles=[], active=True):
    if form.validate_on_submit():
        usersfile = read_file(jsonpath)
        print(usersfile)
        if usersfile.get(form.name.data):
            return False
        user = {
        'active': active,
        'roles': roles,
        'authentication_method': authentication_method,
        'authenticated': False
        }
        if authentication_method == 'hash':
            user['hash'] = 'bah'
            # make_salted_hash(password)
        elif authentication_method == 'cleartext':
            user['password'] = form.password.data
        else:
            raise NotImplementedError(authentication_method)
        usersfile[form.name.data] = user
        print(usersfile)
        write_file(jsonPath, usersfile)
        response = usersfile.get(form.name.data)
        return response
    else:
        return False


def delete_user(form, jsonpath, username):
    if form.validate_on_submit:
        usersfile = read_file(jsonpath)
        credentialscheck = usersfile.get(username)
        if credentialscheck.get('password') == form.id.data:
            if not usersfile.pop(form.name.data):
                return False
        write_file(jsonpath, usersfile)
        return True


def delete_users_by_role(jsonpath, role):
    if not os.path.exists(jsonpath):
        return False
    usersfile = read_file(jsonpath)
    for u in xrange(len(usersfile)):
        if role in usersfile[u].get('roles'):
            if not usersfile.pop(usersfile[u].get('name')):
                return False
    write_file(jsonpath, usersfile)
    return usersfile


def read_file(jsonpath):
    with open(jsonpath, "r") as f:
        data = json.loads(f.read())
    return data


def write_file(jsonpath, data):
    with open(jsonpath, 'w') as f:
        f.write(json.dumps(data, indent=2))
