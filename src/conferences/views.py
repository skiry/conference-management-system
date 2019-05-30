from __future__ import unicode_literals
from braces import views as bracesviews
from django import forms as django_forms
from django.shortcuts import render
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
        actors_conference = actor.conference_set.filter(id = conf_id).first()
        this_conference = models.Conference.objects.filter(id = conf_id).first()

        # if this conference does not exist.
        if this_conference is None:
            return super().form_invalid(form)

        # if this user is chairing this conference... then they can't submit
        if actors_conference is not None:
            return super().form_invalid(form)

        # Or if we're beyond the time for submitting abstracts...
        if this_conference.abstractDate <= datetime.date.today():
            return super().form_invalid(form)

        models.Submission(
            abstract = data['abstract'],
            fullPaper = data['fullPaper'],
            metaInfo = data['metaInfo'],
            submitter = actor,
            conference = this_conference
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
        actors_conference = actor.conference_set.filter(id = conf_id).first()
        this_conference = models.Conference.objects.filter(id = conf_id).first()

        # if this conference does not exist...
        if this_conference is None:
            return super().form_invalid(form)

        # if this user is chairing this conference... then they can't submit
        if actors_conference is not None:
            return super().form_invalid(form)

        # if this user is already a pc member in this conference... then he can't submit
        if this_conference.pcmemberin_set.filter(actor_id = actor.id).first() is not None:
            return super().form_invalid(form)

        models.PcMemberIn(
            description = data['description'],
            actor = actor,
            conference = this_conference
        ).save()

        return super().form_valid(form)

class Submissions(Abstract):
    template_name = "conferences/submissions.html"

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)
        context['submissions'] = models.Submission.objects.filter(conference_id = self.kwargs['conference_id'])
        return context

class SpecificSubmission(Abstract):
    template_name = "conferences/specific-submission.html"

    def dispatch(self, request, *args, **kwargs):
        submission = models.Submission.objects.filter(id = self.kwargs['submission_id']).first()
        actor = models.loggedActor(self)

        # if submission doesn't exist...
        if submission is None:
            return reverse_lazy("conferences")

        # if the actor isn't a pc member for this conference...
        if actor.pcmemberin_set.filter(conference_id = submission.conference.id).first() is None:
            return reverse_lazy("conferences")

        return render(request, SpecificSubmission.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)

        submission = models.Submission.objects.get(pk = self.kwargs['submission_id'])
        biddings = list(submission.bidding_set.all())

        for x in biddings:
            x.bid = x.getBid()

        context['submission'] = submission
        context['biddings'] = biddings
        context['remarks'] = list(submission.submissionremark_set.all())
        return context

class BidSubmission(FormView, Abstract):
    template_name = "conferences/bid-submission.html"
    form_class = forms.BidSubmission
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        submission_id = self.kwargs['submission_id']

        actor = models.loggedActor(self)
        this_submission = models.Submission.objects.filter(id = submission_id).first()

        # if this conference does not exist.
        if this_submission is None:
            return super().form_invalid(form)

        this_conference = this_submission.conference
        pcmemberin = this_conference.pcmemberin_set.filter(actor_id = actor.id).first()

        # if this actor is not a pc member in this conference...
        if pcmemberin is None:
            return super().form_invalid(form)

        # if this actor has already bid on this submission...
        if models.SubmissionRemark.objects.filter(submission_id = this_submission.id).filter(pcmember_id = pcmemberin.id).first() is not None:
            return super().form_invalid(form)

        models.Bidding(
            submission = this_submission,
            pcmember = pcmemberin,
            bid = data['bidding']
        ).save()

        return super().form_valid(form)


class CommentSubmission(FormView, Abstract):
    template_name = "conferences/comment-submission.html"
    form_class = forms.CommentSubmission
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        submission_id = self.kwargs['submission_id']

        actor = models.loggedActor(self)
        this_submission = models.Submission.objects.filter(id = submission_id).first()

        # if this conference does not exist.
        if this_submission is None:
            return super().form_invalid(form)

        this_conference = this_submission.conference
        pcmemberin = this_conference.pcmemberin_set.filter(actor_id = actor.id).first()

        # if this actor is not a pc member in this conference...
        if pcmemberin is None:
            return super().form_invalid(form)

        models.SubmissionRemark(
            submission = this_submission,
            pcmember = pcmemberin,
            content = data['remark']
        ).save()

        return super().form_valid(form)

# TODO:
# 1 - pass through the context all the names of all the submissions
#   - that is to put them in the headers
# 2 - in the same order, for each member, have its bidding result shown
# 3 - make the bidding result clickable - clicking it means assign to pc member x submission y for review.
# ordering the submissions by the id should do it.

class PcMembersPanel(Abstract):
    template_name = "conferences/pc-members-panel.html"

    def dispatch(self, request, *args, **kwargs):
        actor = models.loggedActor(self)
        conf_id = self.kwargs['conference_id']
        this_conference = models.Conference.objects.filter(id = conf_id).first()

        # if this conference does not exist.
        if this_conference is None:
            return reverse_lazy("conferences")

        # if this user is not the chair...
        if actor.conference_set.filter(id = conf_id).first() is None:
            return reverse_lazy("conferences")

        return render(request, PcMembersPanel.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)

        actor = models.loggedActor(self)
        conf_id = self.kwargs['conference_id']
        this_conference = models.Conference.objects.filter(id = conf_id).first()

        context['members'] = this_conference.pcmemberin_set.all()
        context['conf'] = this_conference
        context['submissions'] = this_conference.submission_set.all()

        return context
