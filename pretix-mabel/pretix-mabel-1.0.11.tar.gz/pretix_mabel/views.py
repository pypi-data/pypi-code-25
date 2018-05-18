import json
from pretix.control.permissions import (
    event_permission_required, EventPermissionRequiredMixin
)
from django.shortcuts import redirect
from django.db.models import Q
from django import forms

from django.views.generic.base import TemplateView, View
from django.core.urlresolvers import resolve, reverse
from pretix.control.views.event import (
    EventSettingsFormView, EventSettingsViewMixin)
from pretix.control.forms.event import (
    InvoiceSettingsForm,
)
from pretix.base.models.event import Event
from pretix.base.models.orders import Order, OrderPosition
from django import forms
from django.utils.translation import ugettext_lazy as _
from pretix.base.forms import SettingsForm
from django.forms import formset_factory, ModelForm, modelformset_factory
from django.contrib import messages
from pretix.base.models.items import Item
from .models import TicketLimit
from django.views.generic import FormView


class MabelSettingsForm(SettingsForm):
    user_sheet_id = forms.CharField(
        label=_("User Sheet ID"),
        required=True,
        help_text=_(
            "Sheet ID for the Google Sheet containing usernames, passwords and user types. "
            "The ID is contained within the URL: https://docs.google.com/spreadsheets/d/##KEY##/edit")
    )
    google_sheets_API_key = forms.CharField(
        label=_("Google Sheets API Key"),
        required=True,
        help_text=_(
            "API Key for Google sheets")
    )
    ibis_proxy_url = forms.CharField(
        label=_("IBIS proxy URL"),
        required=True,
        help_text=_(
            "For example, http://emmamayball.com/ibis")
    )
    ibis_institution_id = forms.CharField(
        label=_("IBIS Institution ID"),
        required=True,
        help_text=_(
            "For Emmanuel College, this should be \"EMMUG\"")
    )


class TicketLimitForm(ModelForm):
    event = forms.HiddenInput()

    class Meta:
        model = TicketLimit
        exclude = []

TicketLimitFormSet = modelformset_factory(
    TicketLimit, exclude=[], can_delete=True)

class StickerSheetForm(forms.Form):
    ticket_type = forms.ModelChoiceField(
        queryset=Item.objects.all(),
        label=_("Ticket Type"),
        required=False,
        help_text=_(
            "Ticket type to print stickers for. "
            "Leave blank to include all types"
            )
    )
    start = forms.IntegerField(
        label=_("Start"),
        required=False,
        help_text=_(
            "Start generating stickers at this ticket number. Effectively skip the first X tickets. "
            "Leave blank to start at the beginning (ticket number 0).")
    )
    end = forms.IntegerField(
        label=_("End"),
        required=False,
        help_text=_(
            "Stop generating stickers after this ticket number. "
            "Leave blank to include all remaining tickets"
            )
    )


class MyTicketsView(EventPermissionRequiredMixin, TemplateView):
    permission = 'can_view_orders'
    template_name = 'pretix_mabel/tickets.html'

    def get_context_data(self, **kwargs):

        apiToken = "2yf5iasohb46bfxpyr7a5pjykjz5540srgqlrwy3qke7r9zuco8qglo2qi689lp7"
        ctx = super().get_context_data(**kwargs)
        print("Event")
        print(self.request.event)

        ticket_type =  self.request.GET.get('ticket_type') 
        start =  self.request.GET.get('start') 
        end =  self.request.GET.get('end') 

        qs = OrderPosition.objects.filter(
                order__event=self.request.event,
            ).filter(
                Q(order__status=Order.STATUS_PENDING) | 
                Q(order__status=Order.STATUS_PAID)
            ).order_by('id')

        if (ticket_type):
            qs = qs.filter(item=ticket_type)

        if (start or end):
            qs = qs[int(start or "0"):int(end or len(qs))]
        

        orders = [{
            "id": x.id,
            "code": x.secret,
            "guest_name": x.attendee_name,
            "ticket_type": str(x.item.name),
            # "meta_info": x.meta_info,
            } for x in qs]

        ctx["tickets"] = json.dumps(orders)
        ctx["ticket_count"] = len(orders)

        ctx["sticker_form"] = StickerSheetForm(self.request.GET)

        return ctx


class MySettingsView(EventSettingsViewMixin, EventSettingsFormView):
    model = TicketLimit
    form_class = MabelSettingsForm
    template_name = 'pretix_mabel/settings.html'
    permission = 'can_change_event_settings'

    def get_success_url(self) -> str:
        return reverse('plugins:pretix_mabel:settings', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug
        })

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ticket_limit_forms"] = TicketLimitFormSet(
            queryset=TicketLimit.objects.filter(event=self.request.event)
        )
        return ctx

    def post(self, request, **kwargs):
        mabel_form = self.get_form()
        formset = TicketLimitFormSet(request.POST)
        if all([formset.is_valid(), mabel_form.is_valid()]):
            formset.save()
            mabel_form.save()
            messages.success(self.request, _('Your changes have been saved. Please note that it can '
                                             'take a short period of time until your changes become '
                                             'active.'))
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, _(
                'We could not save your changes. See below for details.'))
            return self.get(request)

