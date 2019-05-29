from __future__ import unicode_literals

from braces import views as bracesviews
from django.views import generic
from django.views.generic import FormView
from django.urls import reverse_lazy

from . import forms
from . import models

class Abstract(bracesviews.LoginRequiredMixin, generic.TemplateView):
    pass

class HomePage(Abstract):
    template_name = "conferences/home.html"

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)
        context['conferences'] = models.Conference.objects.all()
        return context

class AddConference(FormView, Abstract):
    template_name = "conferences/conference-add.html"
    form_class = forms.AddConference
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        _id = self.request.user.id

        models.Conference(
            name = data['name'],
            website = data['website'],
            info = data['info'],
            startDate = data['startDate'],
            abstractDate = data['abstractDate'],
            submissionDate = data['submissionDate'],
            presentationDate = data['presentationDate'],
            endDate = data['endDate'],
            chairedBy = models.Actor.objects.all().filter(user_id = _id).first()
        ).save()

        return super().form_valid(form)
