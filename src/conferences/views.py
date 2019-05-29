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

class SubmitProposal(FormView, Abstract):
    template_name = "conferences/submit-proposal.html"
    form_class = forms.SubmitProposal
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        conf_id = self.kwargs['conference_id']
        actor = models.loggedActor(self)
        this_conference = actor.conference_set.get(pk = conf_id)

        # if this user is chairing this conference... then they can't submit
        if this_conference is not None:
            return super().form_invalid(form)

        # Or if we're beyond the time for submitting abstracts...
        if this_conference.abstractDate <= datetime.date.today():
            return super().form_invalid(form)

        models.Submission(
            abstract = data['abstract'],
            fullPaper = data['fullPaper'],
            metaInfo = data['metaInfo'],
            submitter = actor
        ).save()

        return super().form_valid(form)

class EnrollPcMember(FormView, Abstract):
    template_name = "conferences/enroll-pcmember.html"
    form_class = forms.EnrollPcMember
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        conf_id = self.kwargs['conference_id']
        actor = models.loggedActor(self)
        this_conference = actor.conference_set.get(pk = conf_id)

        # if this user is chairing this conference... then they can't submit
        # if this_conference is not None:
        #     return super().form_invalid(form)

        models.PcMemberIn(
            description = data['description'],
            actor = actor,
            conference = this_conference
        ).save()

        return super().form_valid(form)
