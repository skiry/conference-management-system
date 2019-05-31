from __future__ import unicode_literals
from django import forms
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field
from . import models

class AddConference(forms.Form):
    name = forms.CharField()
    website = forms.CharField()
    info = forms.CharField()

    start_date = forms.DateField()
    abstract_date = forms.DateField()
    submission_date = forms.DateField()
    presentation_date = forms.DateField()
    end_date = forms.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field("name", placeholder = "Name"),
            Field("website", placeholder = "Website"),
            Field("info", placeholder = "Information"),
            Field("start_date", placeholder="Starting Date"),
            Field("abstract_date", placeholder="Abstract Deadline Date"),
            Field("submission_date", placeholder="Submission Deadline Date"),
            Field("presentation_date", placeholder="Presentation Deadline Date"),
            Field("end_date", placeholder = "Ending Date"),
            Submit("create_conference", "Create new conference", css_class="btn btn-lg btn-primary btn-block"),
        )

class SubmitProposal(forms.Form):
    title = forms.CharField(max_length = 128)
    abstract = forms.CharField(max_length = 2550)
    full_paper = forms.CharField(max_length=25500, required=False)
    meta_info = forms.CharField(max_length=10000, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field("title", placeholder = "Paper Title"),
            Field("abstract", placeholder = "Paper Abstract"),
            Field("full_paper", placeholder="Full Paper"),
            Field("meta_info", placeholder="General Information Behind the Paper"),
            Submit("submit_proposal", "Submit your proposal", css_class="btn btn-lg btn-primary btn-block")
        )

class EnrollPcMember(forms.Form):
    description = forms.CharField(max_length = 1024)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field("description", placeholder = "Why would you be a good PC Member?"),
            Submit("submit_enrollment", "Submit your proposal", css_class="btn btn-lg btn-primary btn-block")
        )

class BidSubmission(forms.Form):
    bidding = forms.ChoiceField(choices = models.BiddingValues.CHOICES, required = True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field("bidding", placeholder = "What's your bidding on this submission?"),
            Submit("submit_bidding", "Submit your bid", css_class="btn btn-lg btn-primary btn-block")
        )

class CommentSubmission(forms.Form):
    remark = forms.CharField(max_length = 1024)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field("remark", placeholder = "What do you have to add?"),
            Submit("submit_remark", "Submit your remark", css_class="btn btn-lg btn-primary btn-block")
        )
