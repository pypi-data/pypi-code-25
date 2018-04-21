from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponse

import traceback, json, datetime

from .decorators import cached_method as _cm, cached_property as _cp
import warnings

class TimeIt():
  def __init__(self):
    self.last = self.start = datetime.datetime.now()
  def __call__(self,s=None):
    now = datetime.datetime.now()
    print s,'\t',int((now-self.start).total_seconds()*1000),'\t',int((now-self.last).total_seconds()*1000)
    self.last = datetime.datetime.now()

def cached_method(*args,**kwargs):
  warnings.warn("Import cached_method from lablackey.decorators, not utils (%s)"%args[0])
  return _cm(*args,**kwargs)

def cached_property(*args,**kwargs):
  warnings.warn("Import cached_property from lablackey.decorators, not utils (%s)"%args[0])
  return _cp(*args,**kwargs)

m = "You are not authorized to do this. If you believe this is in error, please contact the webmaster."

FORBIDDEN = HttpResponseForbidden(m)

JsonResponse = lambda data,*args,**kwargs: HttpResponse(json.dumps(data),*args,**kwargs)

def get_admin_url(self):
  _meta = self._meta
  return reverse("admin:%s_%s_change"%(_meta.app_label, _meta.model_name), args=(self.id,))

def reset_password(user,
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt'):
  form = PasswordResetForm({'email':user.email})
  if form.is_valid():
    form.save(
      subject_template_name=subject_template_name,
      email_template_name=email_template_name)
    
  else:
    print form.errors

def get_or_none(model,**kwargs):
  try:
    return model.objects.get(**kwargs)
  except model.DoesNotExist:
    return None
  except model.MultipleObjectsReturned:
    return model.objects.filter(**kwargs)[0]

xlate={
  0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A', 0xc6:'Ae', 0xc7:'C',
  0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E', 0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I',
  0xd0:'Th', 0xd1:'N', 0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
  0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U', 0xdd:'Y', 0xde:'th', 0xdf:'ss', 0xe0:'a',
  0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a', 0xe6:'ae', 0xe7:'c', 0xe8:'e',
  0xe9:'e', 0xea:'e', 0xeb:'e', 0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i', 0xf0:'th',
  0xf1:'n', 0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o', 0xf9:'u',
  0xfa:'u', 0xfb:'u', 0xfc:'u', 0xfd:'y', 0xfe:'th', 0xff:'y', 0xa1:'!', 0xa2:'{cent}',
  0xa3:'{pound}', 0xa4:'{currency}', 0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}',
  0xa8:'{umlaut}', 0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}', 0xad:'-',
  0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}', 0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}',
  0xb4:"'", 0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}',
  0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>',  0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}',
  0xbf:'?', 0xd7:'*', 0xf7:'/'
}

def latin1_to_ascii (unicrap):
  """This takes a UNICODE string and replaces Latin-1 characters with
    something equivalent in 7-bit ASCII. It returns a plain ASCII string. 
    This function makes a best effort to convert Latin-1 characters into 
    ASCII equivalents. It does not just strip out the Latin-1 characters.
    All characters in the standard 7-bit ASCII range are preserved. 
    In the 8th bit range all the Latin-1 accented letters are converted 
    to unaccented equivalents. Most symbol characters are converted to 
    something meaningful. Anything not converted is deleted.
  """
  try:
    return unicode(unicrap)
  except:
    pass
  r = ''
  for i in unicrap:
    if xlate.has_key(ord(i)):
      r += xlate[ord(i)]
    elif ord(i) >= 0x80:
      pass
    else:
      r += str(i)
  return r
