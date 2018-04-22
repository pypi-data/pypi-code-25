from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import get_template

from mdmail.api import EmailContent


def send_mail(subject, message, from_email, recipient_list, context=None, request=None, fail_silently=False,
              css=None, image_root='.', auth_user=None, auth_password=None, connection=None):
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    if context is not None:
        message = get_template(message).render(context, request)
    content = EmailContent(message, css=css, image_root=image_root)
    mail = EmailMultiAlternatives(subject, content.text, from_email, recipient_list, connection=connection)
    mail.attach_alternative(content.html, 'text/html')

    return mail.send()
