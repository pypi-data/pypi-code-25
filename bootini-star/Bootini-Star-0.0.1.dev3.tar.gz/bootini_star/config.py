"""
Configuration for development, testing and production environments is handled
using different objects. These objects inspect environment variables. Settings
should be overridden by using these env variables.
"""
__author__ = 'Ralph Seichter'

import os

BAD = 'bad'
DEVELOPMENT_DB_URI = 'postgresql://postgres:@localhost/bs'
TEST_DB_URI = DEVELOPMENT_DB_URI + '_test'


class Config(object):
    """
    Configuration object base class.

    If you need to change settings like ESI_CALLBACK_URI to address
    local requirements, use environment variables.
    """
    SECRET_KEY = os.getenv('SECRET_KEY', BAD)
    ESI_CLIENT_ID = os.getenv('ESI_CLIENT_ID', BAD)
    ESI_SECRET_KEY = os.getenv('ESI_SECRET_KEY', BAD)
    ESI_CALLBACK_URI = os.getenv(
        'ESI_CALLBACK_URI', 'http://127.0.0.1:5000/sso/callback')
    OAUTH_BASE = 'https://login.eveonline.com/oauth/'
    ESI_AUTHORIZATION_URI = OAUTH_BASE + 'authorize'
    ESI_TOKEN_URI = OAUTH_BASE + 'token'
    ESI_VERIFY_URI = OAUTH_BASE + 'verify'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False


class Development(Config):
    """Enable debugging during development."""
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = DEVELOPMENT_DB_URI


class Testing(Config):
    """Override Flask server name during local testing."""
    DEBUG = True
    TESTING = True
    SERVER_NAME = 'Argon.local'
    SQLALCHEMY_DATABASE_URI = TEST_DB_URI


class Production(Config):
    """Use environment variables to define your production settings."""
    SQLALCHEMY_DATABASE_URI = 'your_db_uri'
    ESI_CALLBACK_URI = 'your_callback_uri'
