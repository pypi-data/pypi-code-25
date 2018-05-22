# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CookieConsentSettings'
        db.create_table(u'django_simple_cookie_consent_cookieconsentsettings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.TextField')(default='This website uses cookies to ensure you get the best experience on our website.')),
            ('button_text', self.gf('django.db.models.fields.CharField')(default='Got it!', max_length=255)),
            ('cookie_policy_link', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('cookie_policy_link_text', self.gf('django.db.models.fields.CharField')(default='Learn more', max_length=255)),
            ('banner_colour', self.gf('django.db.models.fields.CharField')(default='#252e39', max_length=255)),
            ('banner_text_colour', self.gf('django.db.models.fields.CharField')(default='#ffffff', max_length=255)),
            ('button_colour', self.gf('django.db.models.fields.CharField')(default='#3acdf6', max_length=255)),
            ('button_text_colour', self.gf('django.db.models.fields.CharField')(default='#ffffff', max_length=255)),
        ))
        db.send_create_signal(u'django_simple_cookie_consent', ['CookieConsentSettings'])


    def backwards(self, orm):
        # Deleting model 'CookieConsentSettings'
        db.delete_table(u'django_simple_cookie_consent_cookieconsentsettings')


    models = {
        u'django_simple_cookie_consent.cookieconsentsettings': {
            'Meta': {'object_name': 'CookieConsentSettings'},
            'banner_colour': ('django.db.models.fields.CharField', [], {'default': "'#252e39'", 'max_length': '255'}),
            'banner_text_colour': ('django.db.models.fields.CharField', [], {'default': "'#ffffff'", 'max_length': '255'}),
            'button_colour': ('django.db.models.fields.CharField', [], {'default': "'#3acdf6'", 'max_length': '255'}),
            'button_text': ('django.db.models.fields.CharField', [], {'default': "'Got it!'", 'max_length': '255'}),
            'button_text_colour': ('django.db.models.fields.CharField', [], {'default': "'#ffffff'", 'max_length': '255'}),
            'cookie_policy_link': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'cookie_policy_link_text': ('django.db.models.fields.CharField', [], {'default': "'Learn more'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'default': "'This website uses cookies to ensure you get the best experience on our website.'"})
        }
    }

    complete_apps = ['django_simple_cookie_consent']