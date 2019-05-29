from django.urls import path
from . import views

# app_name = "conferences"
urlpatterns = [
    path("", views.HomePage.as_view(), name="conferences"),
    path("add", views.AddConference.as_view(), name='add-conference'),
]
