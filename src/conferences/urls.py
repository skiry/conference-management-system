from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomePage.as_view(), name="conferences"),
    path("add/", views.AddConference.as_view(), name='add-conference'),
    path("<int:conference_id>/propose", views.SubmitProposal.as_view(), name='submit-proposal'),
]
