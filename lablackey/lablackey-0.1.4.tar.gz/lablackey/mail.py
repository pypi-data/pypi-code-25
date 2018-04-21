from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail, mail_admins
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import get_template, TemplateDoesNotExist
from django.template import Context, RequestContext
from cStringIO import StringIO

import sys, traceback

try:
  import markdown
  import html2text
except ImportError:
  pass

def render_template(name,context):
  html = None
  tried = []
  for ext in ['html','md']:
    try:
      html = get_template("%s.%s"%(name,ext)).render(context)
      tried.append("%s.%s"%(name,ext))
      break
    except TemplateDoesNotExist:
      pass
  if html and ext == 'md':
    html = markdown.markdown(html, extensions=['lablackey.mdx_urlize','markdown.extensions.nl2br'], safe_mode=True)
  text = None
  try:
    text = get_template("%s.txt"%name).render(context)
    tried.append("%s.%s"%(name,ext))
  except TemplateDoesNotExist:
    pass
  if not html and not text:
    raise TemplateDoesNotExist("Tried: %s"%tried)
  if not text:
    _h = html2text.HTML2Text()
    _h.body_width=0
    text = _h.handle(html)
  return html,text

def send_template_email(template_name, recipients, request=None,
                        from_email=settings.DEFAULT_FROM_EMAIL, context={},bcc=[]):
  if type(recipients) in [unicode,str]:
    recipients = [recipients]
  if not 'settings' in context:
    context['settings'] = {a: getattr(settings,a,None) for a in getattr(settings,"PUBLIC_SETTINGS",['DEBUG'])}
  preface = ''
  html,text = render_template(template_name,context)
  msg = EmailMultiAlternatives(
    get_template('%s.subject'%template_name).render(context).strip(), # dat trailing linebreak
    text,
    from_email,
    recipients,
    bcc=bcc,
  )
  if html:
    msg.attach_alternative(html, "text/html")
  msg.send()
  return html,text

admin = None
if settings.ADMINS:
  admin = [settings.ADMINS[0][1]]

def print_to_mail(subject='Unnamed message',to=admin,notify_empty=lambda:True):
  def wrap(target):
    def wrapper(*args,**kwargs):
      old_stdout = sys.stdout
      sys.stdout = mystdout = StringIO()
      mail_on_fail(target)(*args,**kwargs)

      sys.stdout = old_stdout
      output = mystdout.getvalue()
      if output:
        send_mail(subject,output,settings.DEFAULT_FROM_EMAIL,to)
      elif notify_empty():
        send_mail(subject,"Output was empty",settings.DEFAULT_FROM_EMAIL,to)

    return wrapper
  return wrap

def mail_on_fail(target):
  def wrapper(*args,**kwargs):
    try:
      return target(*args,**kwargs)
    except Exception, err:
      lines = [
        "An unknown erro has occurred when executing the following function:",
        "name: %s"%target.__name__,
        "args: %s"%args,
        "kwargs: %s"%kwargs,
        "",
        "traceback:\n%s"%traceback.format_exc(),
        ]
      mail_admins("Error occurred via 'mail_on_fail'",'\n'.join(lines))
  return wrapper

def filter_emails(emails):
  if settings.DEBUG:
    #only email certain people from dev server!
    return [e for e in emails if e in getattr(settings,'ALLOWED_EMAILS',[])]

class DebugBackend(EmailBackend):
  def send_messages(self,email_messages):
    if not settings.DEBUG and not getattr(settings,"DEBUG_EMAIL",False):
      return super(DebugBackend,self).send_messages(email_messages)
    for message in email_messages:
      if not settings.EMAIL_SUBJECT_PREFIX in message.subject:
        message.subject = "%s%s"%(settings.EMAIL_SUBJECT_PREFIX,message.subject)
      attrs = ['to','cc','bcc']
      original = {a:getattr(message,a) for a in attrs}
      message.to = filter_emails(message.to) or [getattr(settings,'ALLOWED_EMAILS',[])[0]]
      message.cc = filter_emails(message.cc)
      message.bcc = filter_emails(message.bcc)
      for a in attrs:
        if getattr(message,a) != original[a]:
          print "%s changed: %s \nfor %s"%(a,original[a],message.subject)
    print "final to: ",message.to
    return super(DebugBackend,self).send_messages(email_messages)
