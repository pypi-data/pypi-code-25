from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.db import transaction
from django.views.generic import UpdateView
from django.contrib import messages
from django.shortcuts import reverse

from optin.forms import UserForm, UserOptinFormSet
from optin.models import UserOptin, Category
from optin.utils import OPTIN_SETTINGS_UPDATE_MESSAGE, USER_MODEL, OPTIN_SETTINGS_UPDATE_MESSAGE_BOOLEAN



# Create your views here.

class UpdateUserOptinView(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    model = USER_MODEL
    template_name = 'optin/optin_form.html'

    def get_context_data(self, **kwargs):
        data = super(UpdateUserOptinView, self).get_context_data(**kwargs)
        
        # ensure we have an option for each Category
        categories = Category.objects.all()

        for category in categories:
            opt, created = UserOptin.objects.get_or_create(user=self.object, category=category)
            if created: opt.save()

        qs = UserOptin.objects.filter(user=self.object)
        
        # create the formset
        if self.request.POST:
            data['formset'] = UserOptinFormSet(self.request.POST)
        else:
            data['formset'] = UserOptinFormSet(queryset=qs)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            formset.save()
            if OPTIN_SETTINGS_UPDATE_MESSAGE_BOOLEAN: messages.add_message(self.request, messages.SUCCESS,OPTIN_SETTINGS_UPDATE_MESSAGE)  
        return super(UpdateUserOptinView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse ('optin:user_opt_selection', kwargs={'pk':self.kwargs['pk']})