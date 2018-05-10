""" The Translation Project system connector. """

import smtplib
from email.message import EmailMessage

from lxml import html
import requests

import datetime
from dateutil.tz import tzlocal
import polib
import re
import os
import shutil
from pathlib import Path

from .entry import POEntry

class TPProject:
    def __init__(self, conf, name, lang, data = {}):
        self.uri = "https://translationproject.org"
        self.conf = conf
        self.name = name
        self.lang = lang
        self.basedir = ''
        self.info = data
        if "version" in data:
            self.version = data['version']

    def open(self, basedir):
        self.basedir = basedir
        self.updateFileName()
        self.updateGettextNames()

    def initialize(self, basedir):
        self.basedir = basedir
        self.updateVersion()
        self.updateFileName()
        self.updateGettextNames()
        self.getpot()
        self.getpo()

    def getpo(self):
        pofile = requests.get('https://translationproject.org/PO-files/' + self.lang + '/' + self.filename)
        if(pofile.status_code == 200):
            with open(self.popath, 'w') as f:
                f.write(pofile.text)
        else:
            shutil.copy(self.potpath, self.popath)

    def getpot(self):
        with open(self.potpath, 'w') as f:
            potfile = requests.get('http://translationproject.org/POT-files/'
                    + self.name + '-' + self.version + '.pot')
            f.write(potfile.text)

    def updateGettextNames(self):
        self.popath = self.basedir + '/' + self.filename
        self.potpath = self.basedir + '/orig.pot'

    def updateVersion(self):
        url = 'https://translationproject.org/domain/' + self.name + '.html'
        page = requests.get(url)
        tree = html.fromstring(page.content)
        pot = tree.xpath('//a[contains(@href,"POT-file")]/text()')
        self.version = re.sub(self.name+'-(.*).pot$', '\\1', str(pot[0]))

    def updateFileName(self):
        self.filename = self.name + '-' + self.version + '.' + self.lang + '.po'

    def update(self, callback):
        oldversion = self.version
        oldname = self.filename
        oldpath = self.popath
        self.updateVersion()
        self.updateFileName()
        self.updateGettextNames()
        self.getpot()
        po = polib.pofile(oldpath)
        po.merge(polib.pofile(self.potpath))
        po.save()
        if oldname == self.filename:
            self.popath = self.popath + '.new.po'
            self.getpo()
            self.popath = oldpath
            self.merge(self.popath + '.new.po', oldpath, callback)
            os.remove(self.popath)
            os.rename(self.popath + '.new.po', self.popath)
        else:
            self.getpo()
            self.merge(self.filename, oldpath, callback)
            os.remove(oldpath)

    def merge(self, tofile, fromfile, callback):
        newpo = polib.pofile(tofile)
        oldpo = polib.pofile(fromfile)
        # If msgid is not found in to file, it's an old one, so ignore.
        # Otherwise, attempt to merge.
        for oentry in oldpo:
            for nentry in newpo:
                if oentry.msgid == nentry.msgid:
                    if oentry.msgstr == nentry.msgstr:
                        break
                    if oentry.msgstr == "":
                        break
                    if nentry.msgstr == "":
                        nentry.msgstr = oentry.msgstr
                        break
                    # else, nentry and oentry have a different msgstr
                    nentry.msgstr = callback(nentry.msgid, oentry.msgstr, nentry.msgstr)
                    break
        newpo.save()

    def send(self, interface):
        self.save()
        msg = EmailMessage()
        msg['Subject'] = self.filename
        msg['From'] = self.conf["email"]
        msg['To'] = 'robot@translationproject.org'
        with open(self.popath, 'rb') as f:
            msg.add_attachment(f.read(), maintype='text', subtype='plain',
                        filename=self.filename)
        with smtplib.SMTP(self.conf['server']+':587') as s:
            s.starttls()
            s.login(self.conf['user'], interface.askPassword())
            s.send_message(msg)

    def save(self):
        self.po.metadata['PO-Revision-Date'] = str(datetime.datetime.now(tzlocal()).__format__("%Y-%m-%d %H:%M%z"))
        self.po.metadata['Last-Translator'] = self.conf['fullname']
        self.po.metadata['Language'] = self.lang
        self.po.metadata['X-Generator'] = 'Offlate 0.1'
        self.po.save()

    def content(self):
        self.po = polib.pofile(self.popath)
        po = [POEntry(x) for x in self.po]
        return {'default': po}
