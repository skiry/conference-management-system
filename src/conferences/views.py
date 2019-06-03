from __future__ import unicode_literals
from braces import views as bracesviews
from django import forms as django_forms
from django.contrib import messages
from django.shortcuts import render
from django.views import generic
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
import datetime

from . import forms
from . import models


def reactToFormAction(evaluate, request):
    if evaluate == "notConferenceChair":
        messages.error(request, 'You are not the chair!')
    elif evaluate == "dateBefore":
        messages.error(request, 'You time-traveller...')
    elif evaluate == "doesNotExist":
        messages.error(request, 'This required item does not exist!')
    elif evaluate == "checkDates":
        messages.error(request, 'Make sure the conference ends after it starts and the abstract\'s '
                                'deadline if before the full paper\'s deadline !')
    elif evaluate == "websiteNotOk":
        messages.error(request, 'Make sure your website is correct ( http://www.[].[]!')
    elif evaluate == "alreadyBid":
        messages.error(request, 'You already have done a bid to this submission!')
    elif evaluate == "alreadyExists":
        messages.error(request, 'Item is already added!')
    else:
        messages.error(request, 'Some error occured!')


class Abstract(bracesviews.LoginRequiredMixin, generic.TemplateView):
    pass


class HomePage(Abstract):
    template_name = "conferences/home.html"

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)
        context['actor'] = models.loggedActor(self)
        context['conferences'] = models.Conference.objects.all()
        return context


class AddConference(FormView, Abstract):
    template_name = "conferences/conference-add.html"
    form_class = forms.AddConference
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data

        conference = models.Conference(
            name=data['name'],
            website=data['website'],
            info=data['info'],
            start_date=data['start_date'],
            abstract_date=data['abstract_date'],
            submission_date=data['submission_date'],
            bidding_date=data['bidding_date'],
            presentation_date=data['presentation_date'],
            end_date=data['end_date'],
            chairedBy=models.loggedActor(self)
        )

        evaluate = conference.checkProposalSubmit()

        if evaluate is "Ok":
            conference.save()
            messages.success(self.request, 'Conference added successfully!')
            return HttpResponseRedirect(reverse_lazy("conferences"))
        else:
            reactToFormAction(evaluate, self.request)
            return self.render_to_response(self.get_context_data(form=form))


class PostponeDeadlines(FormView, Abstract):
    template_name = "conferences/postpone-deadlines.html"
    form_class = forms.PostponeDeadlines
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        conf_id = self.kwargs['conference_id']
        actor = models.loggedActor(self)
        this_conference = models.Conference.objects.get(id=conf_id)

        evaluate = [actor.isConferenceChair(conf_id), this_conference.isNewDateAfterCurrent(data)]

        if evaluate.count("Ok") != len(evaluate):
            for evaluation in evaluate:
                if evaluation != "Ok":
                    reactToFormAction(evaluation, self.request)
                    return self.render_to_response(self.get_context_data(form=form))
        else:
            this_conference.updateDates(data)
            messages.success(self.request, 'Deadlines postponed successfully!')
            return super(PostponeDeadlines, self).form_valid(form)


class SubmitProposal(FormView, Abstract):
    template_name = "conferences/submit-proposal.html"
    form_class = forms.SubmitProposal
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        conf_id = self.kwargs['conference_id']
        actor = models.loggedActor(self)
        actors_conference = actor.conference_set.filter(id=conf_id).first()
        this_conference = models.Conference.objects.filter(id=conf_id).first()

        correct = 0
        # if this conference does not exist.
        if this_conference is None:
            correct = 1

        # if this user is chairing this conference... then they can't submit
        if actors_conference is not None:
            correct = 2

        # Or if we're beyond the time for submitting abstracts...
        if this_conference.abstract_date <= datetime.date.today():
            correct = 3

        if correct == 0:
            models.Submission(
                title=data['title'],
                abstract=data['abstract'],
                full_paper=data['full_paper'],
                meta_info=data['meta_info'],
                submitter=actor,
                conference=this_conference
            ).save()
            messages.success(self.request, 'You have successfully posted your submission!')
            return super(SubmitProposal, self).form_valid(form)
        elif correct == 2:
            messages.error(self.request, 'You are the chair! You cannot submit a proposal!')
        elif correct == 3:
            messages.error(self.request, 'Unfortunately is too late!')
        else:
            messages.error(self.request, 'Some error occured!')

        return self.render_to_response(self.get_context_data(form=form))


class CreateSection(FormView, Abstract):
    template_name = "conferences/create-section.html"
    form_class = forms.CreateSection
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data

        if not models.Section.alreadyExists(data['section_name']):
            models.Section(
                name=data['section_name']
            ).save()
            messages.success(self.request, 'You have successfully added this section!')
            return super(CreateSection, self).form_valid(form)
        else:
            messages.error(self.request, 'Section already exists')

        return self.render_to_response(self.get_context_data(form=form))


class AddSectionToConference(FormView, Abstract):
    template_name = "conferences/add-section-conference.html"
    form_class = forms.AddSectionToConference
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        conf_id = self.kwargs['conference_id']
        this_conference = models.Conference.objects.filter(id=conf_id).first()
        section_name = data['section_name']
        actor = models.loggedActor(self)

        evaluate = [this_conference.isChairedBy(actor), models.Section.exists(section_name),
                    this_conference.hasSection(section_name)]

        if evaluate.count("Ok") != len(evaluate):
            for evaluation in evaluate:
                if evaluation != "Ok":
                    reactToFormAction(evaluation, self.request)
                    return self.render_to_response(self.get_context_data(form=form))
        else:
            this_conference.sections.add(models.Section.objects.get(name=section_name))
            messages.success(self.request, 'You have successfully added this tag to your conference!')
            return super(AddSectionToConference, self).form_valid(form)


class EnrollPcMember(FormView, Abstract):
    template_name = "conferences/enroll-pcmember.html"
    form_class = forms.EnrollPcMember
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        conf_id = self.kwargs['conference_id']
        actor = models.loggedActor(self)
        actors_conference = actor.conference_set.filter(id=conf_id).first()
        this_conference = models.Conference.objects.filter(id=conf_id).first()

        correct = 0
        # if this conference does not exist...
        if this_conference is None:
            correct = 1

        # if this user is chairing this conference... then they can't submit
        if actors_conference is not None:
            correct = 2

        # if this user is already a pc member in this conference... then he can't submit
        elif this_conference.pcmemberin_set.filter(actor_id=actor.id).first() is not None:
            correct = 3

        if correct == 0:
            models.PcMemberIn(
                description=data['description'],
                actor=actor,
                conference=this_conference
            ).save()
            messages.success(self.request, 'You are successfully enrolled!')
            return super(EnrollPcMember, self).form_valid(form)
        elif correct == 2:
            messages.error(self.request, 'I see what you\'re doing.. haha you little cheater!')
        elif correct == 3:
            messages.error(self.request, 'You\'d better create a clone if you want to be a PC member twice!')
        else:
            messages.error(self.request, 'Some error occured!')

        return self.render_to_response(self.get_context_data(form=form))


class Submissions(Abstract):
    template_name = "conferences/submissions.html"

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)
        context['submissions'] = models.Submission.objects.filter(conference_id=self.kwargs['conference_id'])
        context['conf'] = models.Conference.objects.filter(id=self.kwargs['conference_id'])[0]
        context['today'] = datetime.date.today
        return context


class ConferencePanel(Abstract):
    template_name = "conferences/conference-panel.html"

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)
        context['conf'] = models.Conference.objects.filter(id=self.kwargs['conference_id'])[0]
        return context


class UpdateSubmission(FormView, Abstract):
    template_name = "conferences/update-submission.html"
    form_class = forms.UpdateSubmission
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        submission_id = self.kwargs['submission_id']
        actor = models.loggedActor(self)
        this_submission = models.Submission.objects.get(id=submission_id)
        this_conference = this_submission.conference
        actors_conference = actor.conference_set.filter(id=this_conference.id).first()
        valid_context = True

        # if this conference does not exist.
        if this_conference is None:
            messages.error(self.request, 'Wrong conference!')
            valid_context = False

        # if this user is chairing this conference... then he can't update submission(proposal)
        if actors_conference is not None:
            messages.error(self.request, 'You are the chair!')
            valid_context = False

        if this_submission is None:
            messages.error(self.request, 'Wrong submission!')
            valid_context = False

        if valid_context:
            this_submission.updateInfo(data)
            messages.success(self.request, 'Update made successfully!')
        return HttpResponseRedirect('/conferences/' + str(this_conference.id) + '/submissions')


class SpecificSubmission(Abstract):
    template_name = "conferences/specific-submission.html"

    def dispatch(self, request, *args, **kwargs):
        submission = models.Submission.objects.filter(id=self.kwargs['submission_id']).first()
        actor = models.loggedActor(self)

        correct = 0
        # if submission doesn't exist...
        if submission is None:
            correct = 1

        # if the actor isn't a pc member for this conference...
        if actor.pcmemberin_set.filter(conference_id=submission.conference.id).first() is None:
            correct = 2

        # if the actor is the author of this submission ( can happen if pc member submits proposal )
        if submission.submitter.id == actor.id:
            correct = 3

        if correct == 0:
            return render(request, SpecificSubmission.template_name, self.get_context_data(**kwargs))
        elif correct == 2:
            messages.error(self.request, 'You are not a PC member!')
        elif correct == 3:
            messages.error(self.request, 'You are the author!')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)

        submission = models.Submission.objects.get(pk=self.kwargs['submission_id'])
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
        this_submission = models.Submission.objects.filter(id=submission_id).first()

        evaluate = []

        this_conference = this_submission.conference
        pcmemberin = this_conference.pcmemberin_set.filter(actor_id=actor.id).first()

        # if this actor is not a pc member in this conference...
        if pcmemberin is None:
            evaluate.append("actorNotPCMember")

        evaluate.append(this_submission.actorIsSubmissionAuthor(actor))

        # if this actor has already bid on this submission...
        if models.Bidding.objects.filter(submission_id=this_submission.id).filter(
                pcmember_id=pcmemberin.id).first() is not None:
            evaluate.append("alreadyBid")

        if evaluate.count("Ok") != len(evaluate):
            for evaluation in evaluate:
                if evaluation != "Ok":
                    reactToFormAction(evaluation, self.request)
                    return HttpResponseRedirect('/conferences/submissions/' + str(submission_id))
        else:
            models.Bidding(
                submission=this_submission,
                pcmember=this_conference.getPCMemberIn(actor),
                bid=data['bidding']
            ).save()
            messages.success(self.request, 'Bid made successfully!')
            return HttpResponseRedirect('/conferences/submissions/' + str(submission_id))


class CommentSubmission(FormView, Abstract):
    template_name = "conferences/comment-submission.html"
    form_class = forms.CommentSubmission
    success_url = reverse_lazy("conferences")

    def form_valid(self, form):
        data = form.cleaned_data
        submission_id = self.kwargs['submission_id']

        actor = models.loggedActor(self)
        this_submission = models.Submission.objects.filter(id=submission_id).first()

        this_conference = this_submission.conference
        evaluate = [this_submission.actorIsSubmissionAuthor(actor), this_conference.actorIsPCMember(actor)]

        if evaluate.count("Ok") != len(evaluate):
            for evaluation in evaluate:
                if evaluation != "Ok":
                    reactToFormAction(evaluation, self.request)
                    return HttpResponseRedirect('/conferences/submissions/' + str(submission_id))
        else:
            models.SubmissionRemark(
                submission=this_submission,
                pcmember=this_conference.getPCMemberIn(actor),
                content=data['remark']
            ).save()
            return HttpResponseRedirect('/conferences/submissions/' + str(submission_id))


class PcMembersPanel(Abstract):
    template_name = "conferences/pc-members-panel.html"

    def dispatch(self, request, *args, **kwargs):
        actor = models.loggedActor(self)
        conf_id = self.kwargs['conference_id']
        this_conference = models.Conference.objects.filter(id=conf_id).first()

        evaluate = this_conference.isChairedBy(actor)

        if evaluate == "Ok":
            messages.success(self.request, 'Permission OK!')
            return render(request, PcMembersPanel.template_name, self.get_context_data(**kwargs))
        else:
            reactToFormAction(evaluate, request)
        return HttpResponseRedirect(reverse_lazy("conferences"))

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)

        actor = models.loggedActor(self)
        conf_id = self.kwargs['conference_id']
        this_conference = models.Conference.objects.filter(id=conf_id).first()

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
        _submission = models.Submission.objects.filter(id=self.kwargs['submission_id']).first()
        _pcmember = models.PcMemberIn.objects.filter(id=self.kwargs['pcmember_id']).first()

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
        if _pcmember.reviewassignment_set.filter(pcmember_id=_pcmember.id).filter(
                submission_id=_submission.id).first() is not None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        models.ReviewAssignment(
            submission=_submission,
            pcmember=_pcmember,
            grade=models.GradingValues.DEFAULT
        ).save()

        return HttpResponseRedirect(reverse_lazy("conferences"))


class ReviewerBoard(Abstract):
    template_name = "conferences/reviewer-board.html"

    def dispatch(self, request, *args, **kwargs):
        actor = models.loggedActor(self)
        conference = models.Conference.objects.filter(id=self.kwargs['conference_id']).first()

        evaluate = conference.isChairedBy(actor)
        if evaluate == "Ok":
            return render(request, ReviewerBoard.template_name, self.get_context_data(**kwargs))
        else:
            reactToFormAction(evaluate, request)
            return HttpResponseRedirect(reverse_lazy("conferences"))

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)

        actor = models.loggedActor(self)
        conference = models.Conference.objects.filter(id=self.kwargs['conference_id']).first()
        pcmemberin = actor.pcmemberin_set.filter(conference_id=conference.id).first()

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

        _submission = models.Submission.objects.filter(id=self.kwargs['submission_id']).first()

        # If the submission is bad.
        if _submission is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        _pcmember = _submission.conference.pcmemberin_set.filter(actor_id=actor.id).first()

        # if the pcmember is bad...
        if _pcmember is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if this pcmember is the chair
        if _pcmember.conference.chairedBy.id == _pcmember.actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if this pcmember submitter this proposal
        if _submission.submitter.id == _pcmember.actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        reviewAssignment = _pcmember.reviewassignment_set.filter(submission_id=_submission.id).first()
        # if this pc member has not been assigned this submssion...
        if reviewAssignment is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        reviewAssignment.grade = grade_index
        reviewAssignment.save()

        return HttpResponseRedirect(reverse_lazy("conferences"))


class Evaluation(Abstract):
    def dispatch(self, request, *args, **kwargs):
        actor = models.loggedActor(self)
        conference = models.Conference.objects.filter(id=self.kwargs['conference_id']).first()

        # if there's no such conference...
        if conference is None:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the current user isn't the chair...
        if conference.chairedBy.id != actor.id:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        # if the conference was already evaluated...
        if conference.evaluated:
            return HttpResponseRedirect(reverse_lazy("conferences"))

        submissions = conference.submission_set.all()
        for submission in submissions:
            for review in submission.reviewassignment_set.all():
                if review.grade == models.GradingValues.DEFAULT:
                    return HttpResponseRedirect(reverse_lazy("conferences"))

        for s in submissions:
            finalGrade = int(sum(list(map(lambda x: x.grade, list(s.reviewassignment_set.all())))))
            models.EvaluationResult(submission=s, grade=finalGrade).save()

        conference.evaluated = True
        conference.save()

        return HttpResponseRedirect(reverse_lazy("conferences"))


class EvaluationResult(Abstract):
    template_name = "conferences/evaluation-result.html"

    def dispatch(self, request, *args, **kwargs):
        actor = models.loggedActor(self)
        conference = models.Conference.objects.filter(id=self.kwargs['conference_id']).first()

        correct = 0
        # if submission doesn't exist...
        if conference is None:
            correct = 1

        if actor.pcmemberin_set.filter(conference_id=conference.id).first() is None:
            correct = 2

        if correct == 0:
            messages.success(self.request, 'Permission OK!')
            return render(request, EvaluationResult.template_name, self.get_context_data(**kwargs))
        elif correct == 1:
            messages.error(self.request, 'The conference does not exist!')
        elif correct == 2:
            messages.error(self.request, 'You are not a PC member!')

        return HttpResponseRedirect(reverse_lazy("conferences"))

    def get_context_data(self, **kwargs):
        context = super(Abstract, self).get_context_data(**kwargs)
        conference = models.Conference.objects.filter(id=self.kwargs['conference_id']).first()

        if conference.evaluated:
            evaluations = list(map(lambda x: x.evaluationresult, conference.submission_set.all()))

            for x in evaluations:
                x.grade = x.getGrade()

            context['evaluations'] = evaluations
        else:
            context['error'] = True
            context['evaluations'] = []

        return context
