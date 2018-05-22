import os
import sys
import click
import click_log
import traceback
import requests
import configparser
import json
import inquirer
from textwrap import indent



CC = 'green' # Config Color
BC = 'yellow' # Bot Color
UC = 'magenta' # User Color
RD = 'red' #Error Color

def echo(msg):
    click.echo(msg.strip())

def reset_color():
    click.echo(click.style('', fg='reset'), nl=False)

base_url = 'https://api.hubtype.com'
#base_url = 'http://localhost:8000'
client_id = 'jOIYDdvcfwqwSs7ZJ1CpmTKcE7UDapZDOSobFmEp'
client_secret = 'YY34FaaNMnIVKztd6LbLIKn3wFqtiLhDgl6ZVyICwsLVWkZN9UzXw0GXFMmWinP3noNGU9Obtb6Nrr1BwMc4IlCTcRDOKJ96JME5N02IGnIY62ZUezMgfeiUZUmMSu68'
#client_id = 'Lj3wp6qFTFc6vOVa1xniDbFcqJm3zf8oTj0Q2kO7'
#client_secret = 'n7qMaTX7ttluNgR54DmVJVxR63mCMWwxlpEI0Q4fVtJ7HRrCbyoPF1mX8crYSQzYMgvDuZ6cPZd76bWk6WwPZUAqeKQrhJUiYCvbv6eAMrSAUUHHmRVTOErMHOMbmZiK'
  


base_api_url = '{}/v1'.format(base_url)
login_url = '{}/o/token/'.format(base_url)
#me_url = '{}/users/me/'.format(base_api_url)
#bots_url = '{}/bots/'.format(base_api_url)
home_path = os.path.expanduser("~")
current_path = os.getcwd()
bot_path = os.path.join(current_path, '.hubtype')
config_path = os.path.join(home_path, '.hubtype')
credentials_path = os.path.join(config_path, 'credentials.ini')

## Check credentials
os.makedirs(config_path, exist_ok=True)
config = configparser.ConfigParser(allow_no_value=True)
config.read(credentials_path)
try:
    access_token = config['DEFAULT']['access_token']
    refresh_token = config['DEFAULT']['refresh_token']
    organization_id = config['ME']['organization_id']
except:
    access_token = None
    refresh_token = None
    organization_id = None

## Check bot
config.read(bot_path)
try:
    bot_id = config['BOT_DEFAULT']['id']
except:
    bot_id = None


def refresh(api_call):
    def func_wrapper(*args, **kwargs):
        try:
            return api_call(*args, **kwargs)
        except requests.exceptions.HTTPError:
            refresh_access_token()
            return api_call(*args, **kwargs)
    return func_wrapper


@refresh
def api_get(path, body=None, **kwargs):
    global access_token, base_api_url
    kwargs['url'] = '{}{}/'.format(base_api_url, path)
    kwargs['data'] = body
    if access_token:
        kwargs.update({'headers': {
            'Authorization': 'Bearer {}'.format(access_token)
        }})
        r = requests.get(**kwargs)
        r.raise_for_status()
        return r.json()
    else:
        click.echo('Please login with \'ht login\'')
        return None


@refresh
def api_post(path, body=None, **kwargs):
    global access_token, base_api_url
    if access_token:
        kwargs['url'] = '{}{}/'.format(base_api_url, path)
        kwargs.update({'headers': {
            'Authorization': 'Bearer {}'.format(access_token)
        }})
        kwargs['data']=body
        r = requests.post(**kwargs)
        r.raise_for_status()
        return r.json()
    else:
        click.echo('Please login with \'ht login\'')
        return None


@refresh
def api_delete(path, **kwargs):
    global access_token, base_api_url
    if access_token:
        kwargs['url'] = '{}{}/'.format(base_api_url, path)
        kwargs.update({'headers': {
            'Authorization': 'Bearer {}'.format(access_token)
        }})
        r = requests.delete(**kwargs)
        r.raise_for_status()
        return r
    else:
        click.echo('Please login with \'ht login\'')
        return None


@refresh
def api_test_bot(text, **kwargs):
    global access_token, bot_id
    kwargs['url'] = '/bots/{}/test_input'.format(bot_id)
    kwargs.update({'headers': {
        'Authorization': 'Bearer {}'.format(access_token)
    }})
    kwargs['data']={'text': text}
    r = requests.post(**kwargs)
    r.raise_for_status()
    return r.json()


@refresh
def api_login(username, password):
    global access_token
    try:
        r = requests.post(login_url, data={
            'username': username,
            'password': password,
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'password'
        })
        credentials = r.json()
        access_token = credentials.get('access_token')
        if access_token:
            me = api_get('/users/me')
            if not me:
                click.echo(click.style('There was a problem login in', fg=RD, bold=True))
                return
            config = configparser.ConfigParser(allow_no_value=True)
            config['DEFAULT'] = credentials
            config['ME'] = me
            with open(credentials_path, 'w') as configfile:
                config.write(configfile)
            return True
    except Exception as e:
        pass
    return False


def refresh_access_token():
    global refresh_token, access_token
    if not refresh_token:
        click.echo(click.style('Please login with \'ht login\'', fg=RD))
        return
    r = requests.post(login_url, data={
        'callback': 'none',
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    })
    credentials = r.json()
    access_token = credentials.get('access_token')
    if access_token:
        config = configparser.ConfigParser(allow_no_value=True)
        config['DEFAULT'] = credentials
        with open(credentials_path, 'w') as configfile:
            config.write(configfile)
    else:
        click.echo(click.style('There was a problem refreshing the access token', fg=RD, bold=True))


def api_logout():
    config = configparser.ConfigParser(allow_no_value=True)
    config['DEFAULT'] = {}
    with open(credentials_path, 'w') as configfile:
        config.write(configfile)

def set_botId():
    click.echo('You need a bot for making a deploy')
    botsList = api_get('/bots', params={'organization_id':organization_id})
    if not botsList:
        click.echo(click.style('There was a problem getting your bots', fg=RD, bold=True))
        return
    bot_id = ask_bot(botsList['results'])
    bot_saved = save_bot_id(bot_id)
    if not bot_saved:
        click.echo(click.style('There was an error saving your bot', fg=RD))
        return None
    return bot_id

def ask_bot(bots):
    bot_map = dict([(b['name'], b['id']) for b in bots])
    confirm_bot = [
        inquirer.Confirm('new_bot',
                      message="Do you want to create a new bot?"),
    ]
    answer_confirm = inquirer.prompt(confirm_bot)
    if not len(bots) and not answer_confirm['new_bot']:
        click.echo(click.style('You don\'t have any bots, please create new one', fg=RD))
    if answer_confirm['new_bot'] or not len(bots):
        bot_name = click.prompt(click.style('Bot name: ', fg=UC, bold=True), type=str,
            prompt_suffix='')
        bot_id = api_post('/bots', {'name': bot_name})['id']
        if bot_id:
            return bot_id
        else:
            click.echo(click.style('There was an error creating the bot', fg=RD))
            return None
    list_bots = [
        inquirer.List('bot_name',
            message="What bot do you want to use?",
            choices=[b['name'] for b in bots],
        ),
    ]
    answers = inquirer.prompt(list_bots)
    if answers is None:
        sys.exit()
    return bot_map.get(answers['bot_name'])

def save_bot_id(bot_id):
    bot = api_get('/bots/{}'.format(bot_id))
    if bot:
        config = configparser.ConfigParser(allow_no_value=True)
        config['BOT_DEFAULT'] = bot
        with open(bot_path, 'w') as configfile:
            config.write(configfile)
        return True
    return False

def print_buttons(element):
    for b in element['buttons']:
        if b['type'] == 'element_share':
            click.echo(click.style(indent('[BUTTON] Share (ShareButton)', ' '*4), fg=BC))
        elif b['type'] == 'web_url':
            click.echo(click.style(indent('[BUTTON] {} ({})'.format(b['title'], b['url']), ' '*4), fg=BC))
        else:
            click.echo(click.style(indent('[BUTTON] {} ({})'.format(b['title'], b['payload']), ' '*4), fg=BC))


def print_elem(element):
    if element['type'] == 'text':
        if element['data'] in ['New session created', 'Session finished']:
            click.echo(click.style(element['data'], fg=RD))
            return
        click.echo(click.style(element['data'], fg=CC))
    elif element['type'] == 'buttonmessage':
        click.echo(click.style(element['text'], fg=CC))
        print_buttons(element)
    elif element['type'] == 'carrousel' or 'list':
        for e in element['elements']:
            click.echo(click.style('-'*20, fg=CC))
            click.echo(click.style(indent(e['title'], ' '*2), fg=CC))
            print_buttons(e)
    else:#TODO create more types of element
        click.echo('TODO: new element --- {}'.format(element))


def print_keyboard(element):
    keyboard = '[quick replies]\n'
    for k in element:
        keyboard += '· {}({})\n'.format(k['label'], k['data'])
    click.echo(click.style(indent(keyboard, ' '*6), fg= CC))


@click.group()
@click.pass_context
def ht(ctx):
    '''
    Hubtype Tools
    '''
    ctx.obj = {
        
    }

@ht.command()
@click.pass_context
def login(ctx):
    '''
    Log in into Hubtype and save credentials
    
    [USAGE] --> ht login
    '''
    email = click.prompt(click.style('email: ', fg=UC, bold=True), type=str,
        prompt_suffix='')
    pwd = click.prompt(click.style('password: ', fg=UC, bold=True), type=str,
        hide_input=True, prompt_suffix='')
    click.echo(click.style('\nLogging in...', fg=UC, bold=True))
    if api_login(email, pwd):
        click.echo(click.style('Success!', fg=CC))
        me = api_get('/users/me')
        click.echo('Hello {}!'.format(me['first_name'] or me['username'] or ''))
        return True
    else:
        click.echo(click.style('Login failed', fg=RD))
        return False


@ht.command()
@click.pass_context
def logout(ctx):
    '''
    Log out from Hubtype

    [USAGE] --> ht logout
    '''
    click.echo('Logging out...')
    api_logout()


@ht.command()
@click.pass_context
def me(ctx):
    '''
    Display 'Hello {YOUR_NAME}'

    [USAGE] --> ht me
    '''
    me = api_get('/users/me')
    if not me:
        click.echo(click.style('There was an error getting the data', fg=RD))
        return
    click.echo('Hello {}!'.format(me['first_name'] or me['username']))

@ht.command()
@click.argument('json_file', required=False)
@click.option('--draft', '-d', is_flag=True, help='Deploy the bot, but don\'t publish it, save as a draft.') #True if --draft it's present
@click.option('--file', '-f', is_flag=True, help='Deploy only a specific file.') #specify an specific file to deploy
@click.pass_context
def deploy(ctx, json_file, draft, file):
    '''
    Deploy your bot to Hubtype.
    By default, it merge all the json files in the current directory and subdirectories,
    and then deploy all of them as one file.

    If you want to deploy a single file, use the flag '--file or -f'
    
    [USAGE] --> ht deploy -f complete_bot.json
    '''
    global access_token, bot_id
    if not access_token:
        click.echo('Please, log in for deploy your bot')
        logingUser = ctx.invoke(login)
        if not logingUser:
            return
    if not bot_id:
        bot_id = set_botId()
    if file:
        file_data = open(json_file, 'r').read()
    else:
        all_files_dir = fileList()
        total_data = {} #final json of all files merged
        for file in all_files_dir:
            try:
                file_o = open(file, 'r').read()
                data = botson_remove_multiline(file_o)
                data = botson_remove_comments(data)
                list_data = json.loads(data)
                total_data = merge(list_data, total_data)
            except Exception as e:
                click.echo('Error in merging all files {}'.format(e))
                pass
        #create json with indent, and don't encode the code
        file_data = json.dumps(total_data, indent=4, sort_keys=True, ensure_ascii=False)
    try:
        bot_draft = api_post('/bots/{}/spec'.format(bot_id), {'spec': file_data})
        if draft and bot_draft['id']:
            click.echo(click.style('Bot saved spec ✅', fg=CC, bold=True))
            return
        bot_publish = api_post('/bots/{}/publish'.format(bot_id))
        if bot_publish['id'] and bot_draft['id']:
            click.echo(click.style('Bot published 🚀', fg=CC, bold=True))
            return
    except Exception as e:
        click.echo(click.style('There was a problem during the deploy: {}'.format(e), 
            fg=RD, bold=True))
        pass

@ht.command()
@click.pass_context
def talk(ctx):
    '''
    Simulate an interactive chat with the bot

    [USAGE] --> ht talk
    '''
    global access_token, bot_id
    if not access_token:
        click.echo('Please, log in for deploy your bot')
        logingUser = ctx.invoke(login)
        if not logingUser:
            return
    if not bot_id:
        bot_id = set_botId()
        ctx.invoke(deploy)
    click.echo('Let\'s talk with your bot:')
    while True:
        user_in = click.prompt(click.style('[you]: ', fg=UC, bold=True), type=str,
        prompt_suffix='')
        res = api_post('/bots/{}/test_input'.format(bot_id), {'text': user_in})
        if not res:
            click.echo(click.style('There was an external error', fg=RD))
        for r in res['messages']:
            print_elem(r)
            try:
                if r['data'] == 'Session finished':
                    return
            except:
                pass
            try:
                print_keyboard(r['keyboard'])
            except:
                pass

@ht.group()
@click.pass_context
def bots(ctx):
    '''
    Part for your bots. Now you can only see all your bots.

    [USAGE] --> ht bots all
    '''
    ctx.obj={}

@bots.command()
@click.pass_context
def all(ctx):
    '''
    List all your bots
    '''
    bots = api_get('/bots', params={'organization_id':organization_id})
    if bots:
        click.echo(click.style('Your bots:', fg=BC, bold=True))
        for b in bots['results']:
            click.echo(click.style(b['name'], fg=UC))

#utils
def botson_remove_comments(botson_string):
    json_string = ""
    for line in botson_string.split('\n'):
        inside_str = False
        prev_char = None
        for i, char in enumerate(line):
            if char == '#' and not inside_str:
                json_string += line[:i] + '\n'
                break
            if char == '"' and prev_char != "\\":
                inside_str = not inside_str
            prev_char = char
            if i == len(line) - 1:
                json_string += line + '\n'
    return json_string

def botson_remove_multiline(botson_string):
    #-----------------Allow multiline-----------------
    multiline = ""
    multilines = 1
    json_string = ""
    for line in botson_string.split('\n'):
        if multiline:
            lstr = line.strip() #Quit first and last whitespaces
        else:
            lstr = line.rstrip() #Quit last whitespaces
        if not lstr:
            continue
        dc = line.count('"')
        cc = line.count('\\"')
        abscom = (dc - cc)
        if len(lstr) and ( abscom%2
            or (multilines > 1 and abscom == 0)): #odd number of " without \" means open string
                                                  #0 absolute " and multiline means line continue
            multiline += lstr + " "
            multilines += 1
        else:
            json_string += multiline+lstr+'\n'*multilines
            multiline = ""
            multilines = 1
    return json_string

def merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            if key == 'states' and type(value) is list:
                try:#because states only array
                    destination[key].extend(value)
                except: #if not exist yet
                    destination[key] = value
            else:
                destination[key] = value

    return destination

def fileList():
    matches = []
    for root, dirnames, filenames in os.walk('.'):
        for filename in filenames: #maybe botson?
            if filename.endswith(('.json', '.JSON')):
                matches.append(os.path.join(root, filename))
    return matches
