import datetime
import hashlib
import random
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _


try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class RegistrationManager(models.Manager):
    def get_and_activate(self, activation_key):
        try:
            profile = self.get(activation_key=activation_key)
        except self.model.DoesNotExist:
            return None, False
        if profile.expired() or profile.activated:
            return profile, False
        user = profile.user
        user.is_active = True
        user.save()
        profile.activated = True
        profile.save()
        return profile,user

    @transaction.atomic
    def create_inactive_user(self, username, email, password, site, send_email=True):
        User = get_user_model()
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        registration_profile = self.create(user=new_user)

        if send_email:
            registration_profile.send_activation_email(site)

        return new_user

    def delete_expired_users(self):
        User = get_user_model()
        for profile in self.filter(expire_date__lte=datetime_now()):
            try:
                user = profile.user
                if not user.is_active:
                    user.delete()
            except User.DoesNotExist:
                pass
            profile.delete()

class RegistrationProfile(models.Model):
    EMPTY_KEY = 'ACTIVATION_KEY'
    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True, verbose_name=_('user'))
    activation_key = models.CharField(_('activation key'), max_length=40,default=EMPTY_KEY)
    expire_date = models.DateTimeField(null=True,blank=True)
    activated = models.BooleanField(default=False)

    objects = RegistrationManager()

    class Meta:
        ordering = ('-id',)

    __unicode__ = lambda self: u"Registration information for %s" % self.user

    expired = lambda self: self.expire_date and self.expire_date < datetime_now()
    expired.boolean = True

    def save(self,*args,**kwargs):
        if self.activation_key == self.EMPTY_KEY:
            self.reset()
        super(RegistrationProfile,self).save(*args,**kwargs)

    def reset(self):
        self.expire_date = datetime_now() + datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        username = self.user.username
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        self.activation_key = hashlib.sha1(salt+username).hexdigest()

    def send_activation_email(self, site):
        ctx_dict = {
            'activation_key': self.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': site,
        }
        subject = render_to_string('registration/activation_email_subject.txt',ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message = render_to_string('registration/activation_email.txt',ctx_dict)

        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
