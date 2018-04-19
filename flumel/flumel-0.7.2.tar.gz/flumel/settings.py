"""
Configuration de l'application

Récupération (et conversion) des infos depuis flumel.config
Pour initialiser la config, dupliquer flumel.config.default en flumel.config
Si le fichier est manquant on tente de récupérer la conf en variables d'environnement
"""

import os
import configparser

try:
    TESTING = os.environ['TESTING']
except KeyError:
    TESTING = False

# pylint: disable=C0103
config = configparser.ConfigParser(interpolation=None)
config.read('flumel.cfg')

try:
    config.get('Instance', 'Name')
except configparser.NoSectionError:
    config.add_section('Instance')
    config.set('Instance', 'Name', os.environ['INSTANCE_NAME'])
    config.set('Instance', 'Url', os.environ['INSTANCE_URL'])
    config.set('Instance', 'Baseline', os.environ['INSTANCE_BASELINE'])

INSTANCE_NAME = config.get('Instance', 'Name')
INSTANCE_URL = config.get('Instance', 'Url')
INSTANCE_BASELINE = config.get('Instance', 'Baseline')

try:
    config.get('Bot', 'Email')
except configparser.NoSectionError:
    config.add_section('Bot')
    config.set('Bot', 'Email', os.environ['BOT_EMAIL'])

BOT_EMAIL = config.get('Bot', 'Email')

try:
    config.get('SMTP', 'Host')
except configparser.NoSectionError:
    config.add_section('SMTP')
    config.set('SMTP', 'Host', os.environ['SMTP_HOST'])
    config.set('SMTP', 'Port', os.environ['SMTP_PORT'])
    config.set('SMTP', 'Login', os.environ['SMTP_LOGIN'])
    config.set('SMTP', 'Password', os.environ['SMTP_PASSWORD'])

BOT_SMTP_HOST = config.get('SMTP', 'Host')
BOT_SMTP_PORT = config.getint('SMTP', 'Port')
BOT_SMTP_LOGIN = config.get('SMTP', 'Login')
BOT_SMTP_PASSWORD = config.get('SMTP', 'Password')

try:
    config.get('IMAP', 'Host')
except configparser.NoSectionError:
    config.add_section('IMAP')
    config.set('IMAP', 'Host', os.environ['IMAP_HOST'])
    config.set('IMAP', 'Port', os.environ['IMAP_PORT'])
    config.set('IMAP', 'Login', os.environ['IMAP_LOGIN'])
    config.set('IMAP', 'Password', os.environ['IMAP_PASSWORD'])

BOT_IMAP_HOST = config.get('IMAP', 'Host')
BOT_IMAP_PORT = config.getint('IMAP', 'Port')
BOT_IMAP_LOGIN = config.get('IMAP', 'Login')
BOT_IMAP_PASSWORD = config.get('IMAP', 'Password')

try:
    config.get('DB', 'Debug')
except configparser.NoSectionError:
    config.add_section('DB')
    config.set('DB', 'Debug', os.environ['DB_DEBUG'])
    config.set('DB', 'Path', os.environ['DB_PATH'])

DEBUG_SQL = config.getboolean('DB', 'Debug')
if TESTING:
    DB_PATH = ':memory:'
else:
    DB_PATH = config.get('DB', 'Path')

try:
    config.get('Queue', 'Path')
except configparser.NoSectionError:
    config.add_section('Queue')
    config.set('Queue', 'Path', os.environ['QUEUE_PATH'])
    config.set('Queue', 'Management', os.environ['QUEUE_MANAGEMENT_PERIOD'])
    config.set('Queue', 'Subscriptions',
               os.environ['QUEUE_SUBSCRIPTIONS_PERIOD'])

if TESTING:
    QUEUE_PATH = ':memory:'
else:
    QUEUE_PATH = config.get('Queue', 'Path')

QUEUE_MANAGEMENT_PERIOD = config.get('Queue', 'Management')
QUEUE_SUBSCRIPTIONS_PERIOD = config.get('Queue', 'Subscriptions')

try:
    config.get('Logging', 'Level')
except configparser.NoSectionError:
    config.add_section('Logging')
    config.set('Logging', 'Level', os.environ['LOGGING_LEVEL'])
    config.set('Logging', 'Path', os.environ['LOGGING_PATH'])

LOGGER_LEVEL = config.get('Logging', 'Level')
LOGGER_PATH = config.get('Logging', 'Path')

try:
    config.get('Keywords', 'Subscribe')
except configparser.NoSectionError:
    config.add_section('Keywords')
    config.set('Keywords', 'Subscribe', os.environ['KEYWORD_SUBSCRIBE'])
    config.set('Keywords', 'Unsubscribe', os.environ['KEYWORD_UNSUBSCRIBE'])

SUBSCRIBE_KEYWORD = config.get('Keywords', 'Subscribe')
UNSUBSCRIBE_KEYWORD = config.get('Keywords', 'Unsubscribe')

REGEX_SUBSCRIBE = '^' + SUBSCRIBE_KEYWORD + r'\s(?P<url>\S+)$'
REGEX_UNSUBSCRIBE = '^' + UNSUBSCRIBE_KEYWORD + r'\s(?P<url>\S+)$'
