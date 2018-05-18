from django.core.urlresolvers import resolve, reverse
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from pretix.control.signals import nav_event_settings, nav_event
from pretix.presale.signals import checkout_flow_steps
from pretix.base.signals import register_payment_providers

from .frontend import MabelStep


@receiver(checkout_flow_steps, dispatch_uid="mabel_checkout_step")
def mabel_checkout_step(sender, **kwargs):
    return MabelStep


@receiver(nav_event_settings, dispatch_uid='mabel_settings')
def mabel_settings(sender, request, **kwargs):
    url = resolve(request.path_info)
    return [
        {
            'label': _('Mabel Settings'),
            'url': reverse('plugins:pretix_mabel:settings', kwargs={
                'event': request.event.slug,
                'organizer': request.organizer.slug,
            }),
            'active': url.namespace == 'plugins:pretix_mabel' and url.url_name == 'settings',
        }
    ]

@receiver(nav_event, dispatch_uid='mabel_navbar')
def mabel_navbar(sender, request, **kwargs):
    url = resolve(request.path_info)
    if not request.user.has_event_permission(request.organizer, request.event, 'can_view_orders'):
        return []
    return [{
        'label': _('Mabel Stickers'),
        'icon': 'qrcode',
        'url': reverse('plugins:pretix_mabel:tickets', kwargs={
            'event': request.event.slug,
            'organizer': request.organizer.slug,
        }),
        'active': url.namespace == 'plugins:pretix_mabel' and url.url_name == 'tickets',
    }]



@receiver(register_payment_providers, dispatch_uid="mabel_college_bill")
def mabel_college_bill(sender, **kwargs):
    from .paymentprovider import CollegeBill
    return CollegeBill


@receiver(register_payment_providers, dispatch_uid="mabel_cheque")
def mabel_cheque(sender, **kwargs):
    from .paymentprovider import Cheque
    return Cheque