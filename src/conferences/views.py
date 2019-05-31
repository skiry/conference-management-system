from __future__ import unicode_literals
from braces import views as bracesviews
from django import forms as django_forms
from django.shortcuts import render
from django.views import generic
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
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
            start_date=data['start_date'],
            abstract_date=data['abstract_date'],
            submission_date=data['submission_date'],
            presentation_date=data['presentation_date'],
            end_date=data['end_date'],
            chairedBy = models.loggedActor(self)
        ).save()

        return super().form_valid(form)


class PostponeDeadlines(FormView, Abstract):
    template_name = "conferences/postpone-deadlines.html"
    form_class = forms.PostponeDeadlines
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        conf_id = self.kwargs['conference_id']
        actor = models.loggedActor(self)
        actors_conference = actor.conference_set.filter(id = conf_id).first()
        this_conference = models.Conference.objects.get(id=conf_id)

        # if this conference does not exist.
        if this_conference is None:
            return super().form_invalid(form)

        # if this user is not chairing this conference... then he can't postpone deadlines
        if actors_conference is None:
            return super().form_invalid(form)

        if this_conference.abstract_date >= data['abstract_date']:
            return super().form_invalid(form)

        if this_conference.submission_date >= data['submission_date']:
            return super().form_invalid(form)

        if this_conference.presentation_date >= data['presentation_date']:
            return super().form_invalid(form)

        if this_conference.end_date >= data['end_date']:
            return super().form_invalid(form)

        this_conference.abstract_date = data['abstract_date']
        this_conference.submission_date = data['submission_date']
        this_conference.presentation_date = data['presentation_date']
        this_conference.end_date = data['end_date']

        this_conference.save()

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
        if this_conference.abstract_date <= datetime.date.today():
            return super().form_invalid(form)

        models.Submission(
            title = data['title'],
            abstract = data['abstract'],
            full_paper = data['full_paper'],
            meta_info = data['meta_info'],
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
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the actor isn't a pc member for this conference...
        if actor.pcmemberin_set.filter(conference_id = submission.conference.id).first() is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the actor is the author of this submission ( can happen if pc member submits proposal )
        if submission.submitter.id == actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        return render(request, SpecificSubmission.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)

        submission = models.Submission.objects.get(pk = self.kwargs['submission_id'])
        biddings = list(submission.bidding_set.all())

        for x in biddings:
            x.bid = x.getBid()

        grades = list(submission.reviewassignment_set.all())
        for x in grades:
            x.grade = x.getGrade()

        context['submission'] = submission
        context['biddings'] = biddings
        context['remarks'] = list(submission.submissionremark_set.all())
        context['grades'] = grades
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

        # if this actor is the author of this submission
        if this_submission.submitter.id == actor.id:
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

        # if this actor is the author of this submission
        if this_submission.submitter.id == actor.id:
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

class PcMembersPanel(Abstract):
    template_name = "conferences/pc-members-panel.html"

    def dispatch(self, request, *args, **kwargs):
        actor = models.loggedActor(self)
        conf_id = self.kwargs['conference_id']
        this_conference = models.Conference.objects.filter(id = conf_id).first()

        # if this conference does not exist.
        if this_conference is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if this user is not the chair...
        if this_conference.chairedBy.id != actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        return render(request, PcMembersPanel.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)

        actor = models.loggedActor(self)
        conf_id = self.kwargs['conference_id']
        this_conference = models.Conference.objects.filter(id = conf_id).first()

        context['conf'] = this_conference

        submissions = this_conference.submission_set.all()
        members = this_conference.pcmemberin_set.all()

        for member in members:
            member.opinions = list(map(lambda x: {'id': x.id, 'value': member.biddingValueFor(x.id)}, submissions))

        context['submissions'] = submissions
        context['members'] = members

        return context

class AssignPcMember(Abstract):
    def dispatch(self, request, *args, **kwargs):
        actor = models.loggedActor(self)
        _submission = models.Submission.objects.filter( id = self.kwargs['submission_id'] ).first()
        _pcmember = models.PcMemberIn.objects.filter(id = self.kwargs['pcmember_id']).first()

        # If the ids are bad.
        if _submission is None or _pcmember is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the pcmember is the chair
        if _pcmember.conference.chairedBy.id == _pcmember.actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the currently logged user is not the chair where the submission was made...
        if _submission.conference.chairedBy.id != actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the pcmember submitter this paper
        if _submission.submitter.id == _pcmember.actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the pcmember is not a member in this conference...
        if _pcmember.conference.id != _submission.conference.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the pcmember has already been assigned for reviewing the submission...
        if _pcmember.reviewassignment_set.filter(pcmember_id = _pcmember.id).filter(submission_id = _submission.id).first() is not None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        models.ReviewAssignment(
            submission = _submission,
            pcmember = _pcmember,
            grade = models.GradingValues.DEFAULT
        ).save()

        return HttpResponseRedirect(reverse_lazy("conferences"))

class ReviewerBoard(Abstract):
    template_name = "conferences/reviewer-board.html"

    def dispatch(self, request, *args, **kwargs):
        actor = models.loggedActor(self)
        conference = models.Conference.objects.filter(id = self.kwargs['conference_id']).first()

        # if the conference does not exist
        if conference is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the actor is not a pc member for the conference...
        if actor.pcmemberin_set.filter(conference_id = conference.id).first() is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        return render(request, ReviewerBoard.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)

        actor = models.loggedActor(self)
        conference = models.Conference.objects.filter(id = self.kwargs['conference_id']).first()
        pcmemberin = actor.pcmemberin_set.filter(conference_id = conference.id).first()

        assignments = pcmemberin.reviewassignment_set.all()

        submissions = list(map(lambda x: x.submission, assignments))

        context['submissions'] = submissions
        context['grades'] = models.GradingValues.CHOICES[1:]

        return context

class GradeSubmission(Abstract):
    def dispatch(self, request, *args, **kwargs):
        actor = models.loggedActor(self)
        grades = models.GradingValues.CHOICES
        grade_index = self.kwargs['grade_index']

        if grade_index < 1 or grade_index >= len(grades):
            return HttpResponseRedirect(reverse_lazy("conferences"))

        _submission = models.Submission.objects.filter( id = self.kwargs['submission_id'] ).first()

        # If the submission is bad.
        if _submission is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        _pcmember = _submission.conference.pcmemberin_set.filter(actor_id = actor.id).first()

        # if the pcmember is bad...
        if _pcmember is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if this pcmember is the chair
        if _pcmember.conference.chairedBy.id == _pcmember.actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if this pcmember submitter this proposal
        if _submission.submitter.id == _pcmember.actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        reviewAssignment = _pcmember.reviewassignment_set.filter(submission_id = _submission.id).first()
        # if this pc member has not been assigned this submssion...
        if reviewAssignment is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        reviewAssignment.grade = grade_index
        reviewAssignment.save()

        return HttpResponseRedirect(reverse_lazy("conferences"))

class Evaluation(Abstract):
    def dispatch(self, request, *args, **kwargs):
        actor = models.loggedActor(self)
        _submission = models.Submission.objects.filter( id = self.kwargs['submission_id'] ).first()
        _pcmember = models.PcMemberIn.objects.filter(id = self.kwargs['pcmember_id']).first()

        # If the ids are bad.
        if _submission is None or _pcmember is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the pcmember is the chair
        if _pcmember.conference.chairedBy.id == _pcmember.actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the currently logged user is not the chair where the submission was made...
        if _submission.conference.chairedBy.id != actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the pcmember submitter this paper
        if _submission.submitter.id == _pcmember.actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the pcmember is not a member in this conference...
        if _pcmember.conference.id != _submission.conference.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the pcmember has already been assigned for reviewing the submission...
        if _pcmember.reviewassignment_set.filter(pcmember_id = _pcmember.id).filter(submission_id = _submission.id).first() is not None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        models.ReviewAssignment(
            submission = _submission,
            pcmember = _pcmember,
            grade = models.GradingValues.DEFAULT
        ).save()

        return HttpResponseRedirect(reverse_lazy("conferences"))


class EvaluationResult(Abstract):
    template_name = "conferences/evaluation-result.html"

    def dispatch(self, request, *args, **kwargs):
        conference = models.Conference.objects.filter(id = self.kwargs['conference_id']).first()

        # if submission doesn't exist...
        if conference is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        return render(request, EvaluationResult.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)
        conference = models.Conference.objects.filter(id = self.kwargs['conference_id']).first()

        if conference.evaluated:
            context['evaluations'] = list(map(lambda x: x.evaluationresult, conference.submission_set.all()))
        else:
            context['error'] = True
            context['evaluations'] = []

        return context
