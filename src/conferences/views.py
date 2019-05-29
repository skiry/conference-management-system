from __future__ import unicode_literals
from braces import views as bracesviews
from django import forms as django_forms
from django.views import generic
from django.views.generic import FormView
from django.urls import reverse_lazy
import datetime

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
            chairedBy = models.loggedActor(self)
        ).save()

        return super().form_valid(form)

# TODO:
# 1. ~~Add buttons on conferences for submitting proposals.~~
# 2. ~~Add validation for submissions to not allow the chair to submit.~~
# 3. Add validation for submission to not allow to submit beyond the submission deadline.

class SubmitProposal(FormView, Abstract):
    template_name = "conferences/submit-proposal.html"
    form_class = forms.SubmitProposal
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        conf_id = self.kwargs['conference_id']

        this_conference = models.loggedActor(self).conference_set.get(pk = conf_id)
        # if this user is chairing this conference... then they can't submit
        if this_conference is not None:
            return super().form_invalid(form)

        # Or if we're beyond the time for submitting abstracts...
        if this_conference.abstractDate <= datetime.datetime.now():
            return super().form_invalid(form)

        models.Submission(
            abstract = data['abstract'],
            fullPaper = data['fullPaper'],
            metaInfo = data['metaInfo'],
            submitter = models.loggedActor(self)
        ).save()

        return super().form_valid(form)
