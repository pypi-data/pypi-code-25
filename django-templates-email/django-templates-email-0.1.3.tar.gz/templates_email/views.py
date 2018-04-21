"""
Views for interactive checking and validation of templates.

You should restrict access if you chose to add them to your urlconf
(for instance with the 'staff_member_required' decorator).
"""

from django import forms
from django.http import HttpResponse, HttpResponseBadRequest

from .helpers import send
from .merge import merge


class PreviewEmailForm(forms.Form):
    template = forms.CharField()
    language = forms.CharField()
    recipient = forms.CharField(required=False)


def preview_email(request):
    """
    Expects 'template' and 'language' querystring parameters.

    If 'recipient' is passed on the querystring then an email will be sent to that recipient,
    otherwise an html page with the email content is displayed.

    All the query string parameters as passed to the template, so you could for instance add
    a ?username=bob to the querystring.
    """
    f = PreviewEmailForm(request.GET)
    if not f.is_valid():
        return HttpResponseBadRequest(f.errors.as_text())

    d = f.cleaned_data
    email_content = merge(
        template_name=d['template'],
        context=request.GET,
        language=d['language']
    )
    recipient = d['recipient']
    if recipient:
        sent_email_count = send(email_content, d['recipient'])
        return HttpResponse('Sent {} emails.'.format(sent_email_count))
    else:
        return HttpResponse(email_content.html)
