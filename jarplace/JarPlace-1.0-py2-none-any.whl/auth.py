def signup(args):
    import webbrowser
    webbrowser.open('https://jar.place/')


def login(args):
    import requests
    from validate_email import validate_email
    from main import HOME
    try:
        with open('%s/.email' % HOME, 'r') as email_file:
            stored_email = email_file.read().strip()
    except FileNotFoundError:
        stored_email = ''
    request = 'Email%s: ' % (' (%s)' % stored_email if stored_email else '')
    email = input(request)
    if not email and stored_email:
        email = stored_email
    while not validate_email(email):
        print('Please, enter valid email address.')
        email = input('Email: ')
    with open('%s/.email' % HOME, 'w') as email_file:
        email_file.write(email)
    response = requests.get('https://repo.jar.place:3333/jwt/obtain', params={'email': email})
    if response.status_code == 401:
        print('It seems like you haven\'t registered yet. '
              'Please, visit https://jar.place/ to sign up for the service or execute \'jarplace signup\'')
        exit(0)
    if response.status_code != 200:
        print('An error occurred, please try again later. Status code:', response.status_code)
        exit(0)
    print('You will receive authentication token via email shortly. Please, enter it below.')
    token = input('Token: ')
    while not token:
        print('Please, enter the token from.')
        token = input('Token: ')
    token = token.strip()
    response = requests.get('https://repo.jar.place:3333/jwt/exchange', headers={'Authorization': 'Bearer ' + token})
    if response.status_code != 200:
        print('An error occurred, please try again later. Status code:', response.status_code)
        exit(0)
    with open('%s/.token' % HOME, 'w') as token_file:
        token_file.write(response.text)
    print(get_token())
    print('Success!')


def get_token():
    from main import HOME
    try:
        with open('%s/.token' % HOME, 'r') as token_file:
            return token_file.read().strip()
    except FileNotFoundError:
        return ''
