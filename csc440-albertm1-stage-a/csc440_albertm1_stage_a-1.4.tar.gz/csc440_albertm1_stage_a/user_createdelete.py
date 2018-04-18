import os
import json


def create_user(form, jsonpath, authentication_method=None, roles=[], active=True):
    """
    create_user opens a json file of user-account data and inserts new user account data into the file, assuming
    that the new user isn't already present in the data-file.
    :param form: A CreateUserForm that was used in the wiki system, which was either imported from this Pypi module
                 user_forms.py, or a custom one with fields "name" and "password".
    :param jsonpath: The full path to the JSON file to be read, including the actual name of the file in the path
    :param authentication_method: Distinct to the wiki440 system, the authentication used in user creation
    :param roles: The roles that are assigned to the user, if needed.
    :param active: User creation, so user will be set to an active new account
    """
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
        if authentication_method == 'cleartext':
            user['password'] = form.password.data
        else:
            raise NotImplementedError(authentication_method)
        usersfile[form.name.data] = user
        print(usersfile)
        write_file(jsonpath, usersfile)
        response = usersfile.get(form.name.data)
        return response
    else:
        return False


def delete_user(form, jsonpath, username):
    """
    delete_user removes a user account and its information from the JSON file of the wiki system.
    :param form: A DeleteUserForm that was used in the wiki system, which was either imported from this Pypi module
                 user_forms.py, or a custom one with field "id" that matches to a user's password.
    :param jsonpath: The full path to the JSON file to be read, including the actual name of the file in the path
    :param username: The name of the account that should be removed from the JSON file of users
    """
    if form.validate_on_submit:
        usersfile = read_file(jsonpath)
        credentialscheck = usersfile.get(username)
        if credentialscheck.get('password') == form.id.data:
            if not usersfile.pop(username):
                return False
        write_file(jsonpath, usersfile)
        return True


def delete_users_by_role(jsonpath, role):
    """
    delete_users_by_role removes all user accounts and their information from the JSON file of the wiki system if they
    have a specific role.
    :param form: A DeleteUserForm that was used in the wiki system, which was either imported from this Pypi module
                 user_forms.py, or a custom one with field "id" that matches to a user's password.
    :param jsonpath: The full path to the JSON file to be read, including the actual name of the file in the path
    :param role: The role name that will qualify user accounts to be deleted from the JSON file
    """
    if not os.path.exists(jsonpath):
        return False
    usersfile = read_file(jsonpath)
    keys = []
    for user, data in usersfile.iteritems():
        for element in data.keys():
            if element == 'roles':
                copy = data[element]
                for r in copy:
                    print(role)
                    if r == role:
                        keys.append(user)
    for u in keys:
        print("\nAttempting to delete user: ", u)
        if not usersfile.pop(u):
            print("\nAn error occurred while trying to delete a user.")
            return False
        print("\nDeleted user successfully!")
    write_file(jsonpath, usersfile)
    return usersfile


def read_file(jsonpath):
    """
    read_file is a simple JSON file reading method
    :param jsonpath: The full path to the JSON file to be read, including the actual name of the file in the path
    """
    with open(jsonpath, "r") as f:
        data = json.loads(f.read())
    return data


def write_file(jsonpath, data):
    """
        read_file is a simple JSON file writing method
        :param jsonpath: The full path to the JSON file to be written to, including the actual name of the file in the
        :param data: The data to be written to the JSON file
        """
    with open(jsonpath, 'w') as f:
        f.write(json.dumps(data, indent=2))
