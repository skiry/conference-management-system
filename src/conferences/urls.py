from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomePage.as_view(), name="conferences"),
    path("add/", views.AddConference.as_view(), name='add-conference'),
    path("<int:conference_id>/postpone", views.PostponeDeadlines.as_view(), name='postpone-deadlines'),
    path("<int:conference_id>/propose", views.SubmitProposal.as_view(), name='submit-proposal'),
    path("<int:conference_id>/enroll", views.EnrollPcMember.as_view(), name='enroll-pcmember'),
    path("<int:conference_id>/submissions", views.Submissions.as_view(), name='submissions'),
    path("submissions/<int:submission_id>", views.SpecificSubmission.as_view(), name='specific-submission'),
    path("submissions/<int:submission_id>/bid", views.BidSubmission.as_view(), name='bid-submission'),
    path("submissions/<int:submission_id>/comment", views.CommentSubmission.as_view(), name='comment-submission'),
    path("<int:conference_id>/pc-members", views.PcMembersPanel.as_view(), name="pc-members-panel"),
    path("submissions/<int:submission_id>/assign/<int:pcmember_id>", views.AssignPcMember.as_view(), name="assign-reviewer"),
    path("<int:conference_id>/reviewer-board", views.ReviewerBoard.as_view(), name="reviewer-board"),
    path("submissions/<int:submission_id>/grade/<int:grade_index>", views.GradeSubmission.as_view(), name="grade-submission"),
    path("<int:conference_id>/evaluate", views.Evaluation.as_view(), name='evaluate'),
    path("<int:conference_id>/evaluation-result", views.EvaluationResult.as_view(), name='evaluation-result'),
]
