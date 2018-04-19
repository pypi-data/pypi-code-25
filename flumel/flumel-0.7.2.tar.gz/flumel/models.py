"""
Modèles de la base de données

* Feed: les flux
* Subscription: les abonnements
* Blacklist: TODO

"""
from datetime import datetime, timedelta

import peewee

from .loggers import logger
from . import settings
from . import tasks

logger.info('Ouverture BDD %s', settings.DB_PATH)
# pylint: disable=C0103
db = peewee.SqliteDatabase(
    settings.DB_PATH, pragmas=(('foreign_keys', 'on'), ))


def stats() -> dict:
    """
    Quelques statistiques de la base de données:
    * feed_count
    * subscription_count
    """
    return {
        'feed_count': Feed.select().count(),
        'subscription_count': Subscription.select().count()
    }


class Feed(peewee.Model):
    """
    Un flux
    """
    url = peewee.TextField(primary_key=True)
    title = peewee.TextField(null=True)
    created_at = peewee.DateTimeField(default=datetime.now)
    sent_at = peewee.DateTimeField(null=True, index=True)
    # @see https://pythonhosted.org/feedparser/http-etag.html
    modified_at = peewee.DateTimeField(null=True, index=True)
    etag = peewee.CharField(null=True, index=True)

    # pylint: disable=R0903
    class Meta:
        """Classement"""
        database = db
        order_by = ('title', )

    def subscribe(self, email: str) -> bool:
        """
        Abonnement de `email` à ce flux
        """
        _, created = Subscription.get_or_create(feed=self, email=email)
        if created:
            logger.debug('[DB] Abonnement de %s à %s', email, self.url)
            tasks.subscribe_success(url=self.url, email=email)
            return True
        logger.debug('[DB] %s déjà abonne à %s', email, self.url)
        tasks.subscribe_duplicate(url=self.url, email=email)
        return False

    def unsubscribe(self, email: str) -> bool:
        """
        Désabonnement de `email` à ce flux. Si plus personne d’abonné on
        delete le flux
        """
        try:
            subscription = Subscription.get(feed=self, email=email)
            subscription.delete_instance()
            logger.debug('[DB] Désabonnement de %s à %s', email, self.url)
            tasks.unsubscribe_success(self.url, email)
            if not self.subscriptions.count():
                logger.info('[DB] Faute d’abonnés, flux %s supprimé', self.url)
                self.delete_instance()
            return True
        except Subscription.DoesNotExist:  # échoue silencieusement
            logger.debug(
                '[DB] Désabonnement de %s à %s impossible car non abonné',
                email, self.url)
            tasks.unsubscribe_failure(self.url, email)
            return False


class Subscription(peewee.Model):
    """
    Un abonnement (un flux + un email)
    """
    feed = peewee.ForeignKeyField(
        Feed, related_name='subscriptions', on_delete='CASCADE')
    email = peewee.TextField()
    created_at = peewee.DateTimeField(default=datetime.now)

    # pylint: disable=R0903
    class Meta:
        """Classement et clé primaire composite feed+email"""
        database = db
        primary_key = peewee.CompositeKey('feed', 'email')
        order_by = ('feed', 'email', 'created_at')


SOFT_RESET_DELAY = 15  # nbre de jours avant RàZ du compteur soft bounce
SOFT_BLOCK_TRIGGER = 29  # nbre de rejets temporaires avant blocage
BLOCK_RESET_DELAY = 6 * 31  # nbre de jours avant RàZ du compteur blocages
BLOCK_RELEASE_DELAY = 14  # nbre de jours avant déblocage
BLOCK_BLACKLIST_TRIGGER = 3  # nbre de blocages avant blacklist


# pylint: disable=R0902
class Bounce(peewee.Model):
    """
    Historique des bounces et mécanisme de blocage en cas d'abus.
    A chaque rejet / blocage on rallonge le délais avant remise à zéro.
    Une tâche vérifie ces délais et réinitialise les compteurs

    Rejets permanents :
    * si 1 avant remise à zéro : blocage
    Rejets temporaires :
    * si 20 avant remise à zéro : blocage

    Si 3 blocages : liste noire définitive définitivement
    """
    email = peewee.TextField(primary_key=True)
    soft_count = peewee.SmallIntegerField(default=0)
    soft_reset_at = peewee.DateTimeField(null=True)
    is_blocked = peewee.BooleanField(default=False, index=True)
    block_count = peewee.SmallIntegerField(default=0)
    block_reset_at = peewee.DateTimeField(null=True)
    block_release_at = peewee.DateTimeField(null=True)
    is_blacklisted = peewee.BooleanField(default=False, index=True)

    # pylint: disable=R0903
    class Meta:
        """classement"""
        database = db

    def soft(self) -> None:
        """
        Incrémentation du compteur des rejets temporaires
        Ràz du compteur 15 jours après le dernier
        """
        if self.is_blocked or self.is_blacklisted:
            return
        if self.soft_count >= SOFT_BLOCK_TRIGGER:
            self.block()
        self.soft_reset_at = datetime.now() + timedelta(days=SOFT_RESET_DELAY)
        self.soft_count += 1
        self.save()

    def release_locks(self) -> None:
        """
        RàZ des compteurs et fin du verrou
        """
        if self.is_blacklisted:
            return
        if self.soft_reset_at < datetime.now():
            self.soft_reset_at = None
            self.soft_count = 0
        if self.block_reset_at < datetime.now():
            self.block_reset_at = None
            self.block_count = 0
        if self.block_release_at < datetime.now():
            self.block_release_at = None
            self.is_blocked = False
        self.save()

    def hard(self) -> None:
        """
        Incrémentation du compteur des rejets permanents
        Ràz du compteur 31 jours après le dernier
        """
        if self.is_blocked or self.is_blacklisted:
            return
        self.block()
        self.save()

    def block(self) -> None:
        """
        Blocage de l'adresse et liste noire si nécessaire
        Ràz des blocages 6 mois après le dernier
        """
        if self.block_count >= 2:
            self.is_blacklisted = True
        self.block_reset_at = datetime.now() + timedelta(
            days=BLOCK_RESET_DELAY)
        self.block_release_at = datetime.now() + timedelta(
            days=BLOCK_RELEASE_DELAY)
        self.block_count += 1
        self.is_blocked = True
        self.save()


logger.info('Création des tables si nécessaire')
db.create_tables([Feed, Subscription, Bounce], safe=True)
