from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomePage.as_view(), name="conferences"),
    path("add/", views.AddConference.as_view(), name='add-conference'),
    path("create-section", views.CreateSection.as_view(), name='create-section'),
    path("<int:conference_id>/postpone", views.PostponeDeadlines.as_view(), name='postpone-deadlines'),
    path("<int:conference_id>/propose", views.SubmitProposal.as_view(), name='submit-proposal'),
    path("<int:conference_id>/enroll", views.EnrollPcMember.as_view(), name='enroll-pcmember'),
    path("<int:conference_id>/submissions", views.Submissions.as_view(), name='submissions'),
    path("<int:conference_id>/conference-submissions", views.ConferenceSubmissions.as_view(), name='user-submissions-panel'),
    path("submissions/<int:submission_id>", views.SpecificSubmission.as_view(), name='specific-submission'),
    path("submissions/<int:submission_id>/updateSubmission", views.UpdateSubmission.as_view(), name='update-submission'),
    path("submissions/<int:submission_id>/bid", views.BidSubmission.as_view(), name='bid-submission'),
    path("submissions/<int:submission_id>/comment", views.CommentSubmission.as_view(), name='comment-submission'),
    path("<int:conference_id>/pc-members", views.PcMembersPanel.as_view(), name="pc-members-panel"),
    path("submissions/<int:submission_id>/assign/<int:pcmember_id>", views.AssignPcMember.as_view(), name="assign-reviewer"),
    path("<int:conference_id>/reviewer-board", views.ReviewerBoard.as_view(), name="reviewer-board"),
    path("submissions/<int:submission_id>/grade/<int:grade_index>", views.GradeSubmission.as_view(), name="grade-submission"),
    path("<int:conference_id>/evaluation-result", views.EvaluationResult.as_view(), name='evaluation-result'),
    path("<int:conference_id>/evaluate", views.Evaluation.as_view(), name='evaluate'),
    path("<int:conference_id>/conference-panel", views.ConferencePanel.as_view(), name='conference-panel'),
    path("<int:conference_id>/add-section-conference", views.AddSectionToConference.as_view(), name='add-section-conference'),
    path("<int:conference_id>/assign-section", views.AssignSection.as_view(), name="assign-section"),
    path("submissions/<int:submission_id>/section-assignment", views.SectionAssignment.as_view(), name="section-assignment"),
    path("submissions/<int:submission_id>/submission-details", views.SubmissionDetails.as_view(), name="submission-details"),
    path("submissions/<int:submission_id>/join", views.JoinPaper.as_view(), name="join-paper")
]
