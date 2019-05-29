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

