from __future__ import unicode_literals
from django import forms
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field

class AddConference(forms.Form):
    name = forms.CharField()
    website = forms.CharField()
    info = forms.CharField()

    startDate = forms.DateField()
    abstractDate = forms.DateField()
    submissionDate = forms.DateField()
    presentationDate = forms.DateField()
    endDate = forms.DateField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field("name", placeholder = "Name"),
            Field("website", placeholder = "Website"),
            Field("info", placeholder = "Information"),
            Field("startDate", placeholder = "Starting Date"),
            Field("abstractDate", placeholder = "Abstract Deadline Date"),
            Field("submissionDate", placeholder = "Submission Deadline Date"),
            Field("presentationDate", placeholder = "Presentation Deadline Date"),
            Field("endDate", placeholder = "Ending Date"),
            Submit("create_conference", "Create new conference", css_class="btn btn-lg btn-primary btn-block"),
        )

class SubmitProposal(forms.Form):
    abstract = forms.CharField(max_length = 255)
    fullPaper = forms.CharField(max_length = 25500, required = False)
    metaInfo = forms.CharField(max_length = 10000, required = False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field("abstract", placeholder = "Paper Abstract"),
            Field("fullPaper", placeholder = "Full Paper"),
            Field("metaInfo", placeholder = "General Information Behind the Paper"),
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
