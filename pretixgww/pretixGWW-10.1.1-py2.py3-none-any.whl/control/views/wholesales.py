from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, CreateView, DeleteView
from django.utils.translation import ugettext as _

from pretix.base.models import Event
from pretix.base.models.wholesale import WholesaleAccount
from pretix.control.forms.wholesales import WholesaleForm
from pretix.control.permissions import EventPermissionRequiredMixin
from pretix.control.views import PaginationMixin, UpdateView


class WholesaleListView(PaginationMixin, EventPermissionRequiredMixin, ListView):
    model = WholesaleAccount
    context_object_name = 'wholesales'
    template_name = 'pretixcontrol/wholesales/index.html'
    permission = 'can_view_wholesales'

    def get_queryset(self):
        qs = self.request.event.wholesales.all()
        return qs.distinct()


class WholesaleCreateView(EventPermissionRequiredMixin, CreateView):
    model = WholesaleAccount
    template_name = 'pretixcontrol/wholesales/detail.html'
    permission = 'can_change_wholesales'
    context_object_name = 'wholesale'
    form_class = WholesaleForm

    def get_form_kwargs(self):
        try:
            kwargs = super().get_form_kwargs()
            kwargs['event'] = Event.objects.get(slug=self.request.event.slug)
        except Event.DoesNotExist:
            kwargs['event'] = None
        return kwargs

    def get_success_url(self):
        return reverse('control:event.wholesales', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug,
        })


class WholesaleUpdateView(EventPermissionRequiredMixin, UpdateView):
    model = WholesaleAccount
    form_class = WholesaleForm
    template_name = 'pretixcontrol/wholesales/detail.html'
    permission = 'can_change_wholesales'
    context_object_name = 'wholesale'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data()
        return ctx

    def get_object(self, queryset=None) -> WholesaleAccount:
        try:
            return self.request.event.wholesales.get(
                id=self.kwargs['id']
            )
        except WholesaleAccount.DoesNotExist:
            raise Http404(_("The requested wholesale does not exist."))

    @transaction.atomic
    def form_valid(self, form):
        messages.success(self.request, _('Your changes have been saved.'))
        if form.has_changed():
            self.object.log_action(
                'pretix.event.wholesales.changed', user=self.request.user, data={
                    k: form.cleaned_data.get(k) for k in form.changed_data
                }
            )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('control:event.wholesales', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug
        })


class WholesaleDeleteView(EventPermissionRequiredMixin, DeleteView):
    model = WholesaleAccount
    template_name = 'pretixcontrol/wholesales/delete.html'
    permission = 'can_change_wholesales'
    context_object_name = 'wholesale'

    def get_object(self, queryset=None):
        try:
            return self.request.event.wholesales.get(
                id=self.kwargs['id']
            )
        except WholesaleAccount.DoesNotExist:
            raise Http404(_("The requested wholesale does not exist."))

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.log_action(action='pretix.event.wholesale.deleted', user=request.user)
        self.object.delete()
        messages.success(self.request, _('The selected wholesale has been deleted.'))
        return HttpResponseRedirect(success_url)

    def get_success_url(self) -> str:
        return reverse('control:event.wholesales', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug,
        })