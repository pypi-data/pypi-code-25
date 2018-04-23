# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Dirk Stöcker <trac@dstoecker.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.

import urllib
import urllib2
from pkg_resources import get_distribution

from trac import __version__ as TRAC_VERSION
from trac.config import Option
from trac.core import Component, implements
from trac.util.html import tag

from tracspamfilter.api import _
from tracspamfilter.captcha import ICaptchaMethod


class RecaptchaCaptcha(Component):
    """reCAPTCHA implementation"""

    implements(ICaptchaMethod)

    private_key = Option('spam-filter', 'captcha_recaptcha_private_key', '',
        """Private key for reCaptcha usage.""", doc_domain="tracspamfilter")

    public_key = Option('spam-filter', 'captcha_recaptcha_public_key', '',
        """Public key for reCaptcha usage.""", doc_domain="tracspamfilter")

    user_agent = 'Trac/%s | SpamFilter/%s' \
                 % (TRAC_VERSION, get_distribution('TracSpamFilter').version)

    def generate_captcha(self, req):
        fragment = tag.script(type='text/javascript',
                              src='https://www.google.com/recaptcha/api/'
                                  'challenge?k=%s' % self.public_key)

        # note - this is not valid XHTML!
        fragment.append(
            tag.noscript(
                tag.iframe(src='https://www.google.com/recaptcha/'
                               'api/noscript?k=%s' % self.public_key,
                           height=300, width=500, frameborder=0),
                tag.br(),
                tag.textarea(name='recaptcha_challenge_field', rows=3, cols=40),
                tag.input(type='hidden', name='recaptcha_response_field',
                          value='manual_challenge'),
                tag.br(),
                tag.input(type='submit', value=_("Submit"))
            )
        )

        return None, fragment

    def encode_if_necessary(self, s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        return s

    def verify_key(self, private_key, public_key):
        if private_key is None or public_key is None:
            return False
        # FIXME - Not yet implemented
        return True

    def verify_captcha(self, req):
        recaptcha_challenge_field = req.args.get('recaptcha_challenge_field')
        recaptcha_response_field = req.args.get('recaptcha_response_field')
        remoteip = req.remote_addr
        try:
            params = urllib.urlencode({
                'privatekey': self.encode_if_necessary(self.private_key),
                'remoteip': self.encode_if_necessary(remoteip),
                'challenge': self.encode_if_necessary(recaptcha_challenge_field),
                'response': self.encode_if_necessary(recaptcha_response_field),
            })
            request = urllib2.Request(
                url='https://www.google.com/recaptcha/api/verify',
                data=params,
                headers={
                    'Content-type': 'application/x-www-form-urlencoded',
                    'User-agent': self.user_agent
                }
            )

            response = urllib2.urlopen(request)
            return_values = response.read().splitlines()
            response.close()
        except Exception, e:
            self.log.warning("Exception in reCAPTCHA handling (%s)", e)
        else:
            if return_values[0] == 'true':
                return True
            else:
                self.log.warning("reCAPTCHA returned error: %s",
                                 return_values[1])
        return False

    def is_usable(self, req):
        return self.public_key and self.private_key
