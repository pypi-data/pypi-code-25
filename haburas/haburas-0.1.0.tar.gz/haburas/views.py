from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from haburas.models import RegistuKursu

# Create your views here.

class Index(ListView):
    model = RegistuKursu
    template_name = "haburas/index.html"

class Create(CreateView):
    model = RegistuKursu
    fields = ['first_name', 'last_name', 'birthday', 'place', 'phonenumber', 'sexo', 'cursu']
    template_name = 'haburas/create.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        self.object = form.save()
        return super(ModelFormMixin, self).form_valid(form)
