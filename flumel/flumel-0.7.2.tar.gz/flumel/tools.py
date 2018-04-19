"""
Boite à outils
"""
import imaplib
import smtplib
from datetime import datetime
from email import message_from_bytes
from email.header import decode_header, make_header
from email.headerregistry import Address
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
from textwrap import shorten
from time import mktime
from xml.sax.saxutils import escape, quoteattr

import html2text
import pkg_resources
import requests
from fake_useragent import UserAgent
from premailer import transform
from readability import Document

from . import settings


def format_template(name: str, **kwargs) -> str:
    """
    Formate le contenu du gabarit `name` avec kwargs + un extrait des settings.
    Utilise `string.Template`, les chaînes `$foo` seront remplacées par la valeur de `foo`.
    On essaye d'utiliser le gabarit personnalisé dans le répertoire `templates/`
    Si introuvable, replis sur celui du package.
    Note: pkg_resources.resource_string est utilisé pour récupérer le path de flumel
    """
    kwargs.update({
        'INSTANCE_NAME': settings.INSTANCE_NAME,
        'INSTANCE_URL': settings.INSTANCE_URL,
        'INSTANCE_BASELINE': settings.INSTANCE_BASELINE,
        'BOT_EMAIL': settings.BOT_EMAIL,
        'SUBSCRIBE_KEYWORD': settings.SUBSCRIBE_KEYWORD,
        'UNSUBSCRIBE_KEYWORD': settings.UNSUBSCRIBE_KEYWORD
    })
    path = '/'.join(['templates', name])
    try:
        with open(path, 'r') as fp_template:
            html = fp_template.read()
    except FileNotFoundError:
        html = pkg_resources.resource_string(__name__, path).decode('utf-8')
    return Template(html).safe_substitute(**kwargs)


def decode_email_header(value) -> str:
    """
    Les headers des emails sont encodés comme des sagouins
    https://docs.python.org/3/library/email.header.html#email.header.decode_header
    @see https://stackoverflow.com/a/12071098
    """
    return str(make_header(decode_header(value))).strip()


def escape_xml(text: str) -> str:
    """
    Échappe les caractères spéciaux d’une chaîne pour intégration dans du xml
    Utilisé pour l’export OPML
    """
    return escape(quoteattr(text))


class Article:
    """
    La synthèse des informations contenues dans le flux RSS et dans ce que
    l’on peut récupérer sur la page de l’article :

    * title - str - champ RSS
    * summary - str - champ RSS
    * body - str - extraction site | champ RSS
    * authors - str - champ RSS
    * date - date - champ RSS
    * link - str - champ RSS
    * keywords - str - champ RSS
    """

    title = ''
    _body = ''
    link = ''
    entry = None

    def __init__(self, entry: object):
        """
        Récupération de la page et dispatch des informations
        """
        self.entry = entry
        self.link = entry.link
        self.title = entry.title
        self.summary = shorten(entry.summary, width=64)

    @property
    def body(self) -> str:
        """
        Tentative de récupération du texte complet de l’article via readability
        Si erreur de récupération de la page on retourne le contenu du flux.
        Si longeur de l’extraction readability > au summary du flux on s'en sert,
        sinon on utilise le flux
        """
        if self._body:  # pseudo cache
            return self._body
        user_agent = UserAgent()
        headers = {'User-Agent': user_agent.ff}
        response = requests.get(self.link, headers=headers)
        if response.status_code != 200:  # lien hs, on retourne le contenu du rss
            self._body = ''
            return self.entry.content[0].value
        try:
            doc = Document(response.text)
            if len(doc.summary()) > len(
                    self.entry.summary):  # extraction > flux
                self._body = doc.summary()
            else:
                self._body = self.entry.summary
            return self._body
        except ValueError:  # erreur dans readability
            self._body = ''
            return self.entry.summary

    @property
    def date(self) -> datetime:
        """
        Retourne la date de publication ou la date de maj
        """
        try:
            return datetime.fromtimestamp(mktime(self.entry.published_parsed))
        except (OverflowError, ValueError):
            return datetime.fromtimestamp(mktime(self.entry.updated_parsed))

    @property
    def authors(self) -> str:
        """
        Ajoute author à contributors et retourne une liste séparée par des virgules
        """
        authors = []
        try:
            authors.append(self.entry.author)
        except AttributeError:
            pass
        try:
            for contributor in self.entry.contributors:
                authors.append(contributor.name)
        except AttributeError:
            pass
        return ', '.join(authors)

    @property
    def keywords(self) -> str:
        """
        Retourne une liste séparée par des virgules des étiquettes / categories
        """
        keywords = []
        try:
            for tag in self.entry.tags:
                keywords.append(tag.label if tag.label else tag.term)
        except AttributeError:
            pass
        return ', '.join(keywords)


class IMAP:
    """
    Interface simplifiée pour imaplib.IMAP4
    La connexion est en SSL si BOT_IMAP_PORT == 993, sinon c'est en starttls
    """

    server = None

    def __init__(self):
        """
        Connexion & login
        """
        if settings.BOT_IMAP_PORT == 993:
            self.server = imaplib.IMAP4_SSL(settings.BOT_IMAP_HOST)
        else:
            self.server = imaplib.IMAP4(settings.BOT_IMAP_HOST)
            self.server.starttls()
        self.server.login(settings.BOT_IMAP_LOGIN, settings.BOT_IMAP_PASSWORD)

    @property
    def inbox(self) -> list:
        """
        Récupération de la liste des messages dans l’inbox, retourne un tableau iterable
        """
        self.server.select()  # ouverture inbox
        _, listing = self.server.search(None, 'ALL')  # (résultat, list)
        return listing[0].split()

    def get(self, number: int):
        """
        Retourne le message `number`
        """
        _, msg = self.server.fetch(number, '(RFC822)')  # (résultat, message)
        return message_from_bytes(msg[0][1])

    def delete(self, number: int):
        """
        Flag le message `number` à supprimer
        """
        return self.server.store(number, '+FLAGS', '\\Deleted')

    def purge(self):
        """
        Vide l’inbox après avoir marqué l’ensemble des messages à supprimer
        """
        for number in self.inbox:
            self.delete(number)
        return self.server.expunge()

    def close(self) -> None:
        """
        Efface les messages avec flag et clôture la connexion
        """
        self.server.select()  # command EXPUNGE only allowed in states SELECTED
        self.server.expunge()
        self.server.close()
        self.server.logout()


class SMTP:
    """
    Interface simplifiée pour smtplib.SMTP
    La connexion est en SSL si BOT_SMTP_PORT == 465, sinon c'est en starttls
    """

    server = None

    def __init__(self):
        """
        Connexion & login
        """
        if settings.BOT_SMTP_PORT == 465:
            self.server = smtplib.SMTP_SSL(settings.BOT_SMTP_HOST,
                                           settings.BOT_SMTP_PORT)
        else:
            self.server = smtplib.SMTP(settings.BOT_SMTP_HOST,
                                       settings.BOT_SMTP_PORT)
            if settings.BOT_SMTP_PORT == 587:
                self.server.starttls()
        try:
            self.server.login(settings.BOT_SMTP_LOGIN,
                              settings.BOT_SMTP_PASSWORD)
        except smtplib.SMTPNotSupportedError:
            pass

    def send(self,
             recipient: str,
             subject: str,
             html: str,
             sender: str = None,
             preheader: str = None,
             **kwargs) -> None:
        """
        Envoi d'un email multipart intégré dans des gabarits
        Le corps du message est envoyé en html et sa conversion en texte brut par html2text
        Les kwargs permettent de personnaliser les entêtes du mail X-Flumel
        par ex. Title="Test" -> X-Flumel-Title = "Test"
        """

        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        if sender:
            message['From'] = str(
                Address(sender, addr_spec=settings.BOT_EMAIL))
        else:
            message['From'] = settings.BOT_EMAIL
        message['To'] = recipient
        # https://docs.python.org/3/library/email.message.html#email.message.EmailMessage.preamble
        if preheader:
            # je pousse présentement des hurlements
            message.preamble = preheader.encode('ascii',
                                                'ignore').decode('utf8')
        if kwargs:
            for key, value in kwargs.items():
                message['X-Flumel-' + key] = value
        # https://stackoverflow.com/a/11797380
        # ajout \n avant le contenu du message
        text = html2text.html2text(html)
        full_txt = format_template('email.txt', **{
            'content': text,
        })
        message.attach(MIMEText('\n' + full_txt, 'plain'))

        full_html = format_template('email.html', **{
            'content': html,
            'preheader': preheader,
            'title': subject
        })
        inline_html = transform(full_html)
        message.attach(MIMEText('\n' + inline_html, 'html'))

        self.server.sendmail(settings.BOT_EMAIL, [recipient],
                             message.as_string())

    def close(self):
        """
        Clôture de la connexion
        """
        self.server.quit()
