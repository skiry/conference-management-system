import re

from django.db import models
from django.contrib.auth import get_user_model

# This is so that we create a new actor each time a user is saved.
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class Actor(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)

    def isConferenceChair(self, conferenceId):
        if self.conference_set.filter(id = conferenceId).first() is None:
            return "notConferenceChair"
        return "Ok"

@receiver(post_save, sender=User)
def _post_save_user_handler(sender, **kwargs):
    Actor(user = kwargs['instance']).save() if kwargs['created'] else None

class Conference(models.Model):
    name = models.CharField(max_length = 255, unique = True)
    website = models.CharField(max_length = 255, unique = True)
    info = models.CharField(max_length = 4096)

    start_date = models.DateField()
    abstract_date = models.DateField()
    submission_date = models.DateField()
    presentation_date = models.DateField()
    end_date = models.DateField()

    chairedBy = models.ForeignKey(Actor, on_delete = models.CASCADE)
    evaluated = models.BooleanField(default = False)

    def isNewDateAfterCurrent(self, data):
        if self is None:
            return "doesNotExist"

        if self.abstract_date >= data['abstract_date']:
            return "dateBefore"

        if self.submission_date >= data['submission_date']:
            return "dateBefore"

        if self.presentation_date >= data['presentation_date']:
            return "dateBefore"

        if self.end_date >= data['end_date']:
            return "dateBefore"

        return "Ok"

    def checkProposalSubmit(self):
        if self is None:
            return "doesNotExist"

        if self.end_date < self.start_date:
            return "checkDates"

        if self.submission_date < self.abstract_date:
            return "checkDates"

        if self.presentation_date < self.start_date \
            or self.presentation_date > self.end_date:
            return "checkDates"

        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        print(re.match(regex, self.website))
        print(re.match(regex, "www.google"))
        print(re.match(regex, "google.com"))
        print(re.match(regex, "www.google.com"))
        if re.match(regex, self.website) is None:
            return "websiteNotOk"

        return "Ok"

    def updateDates(self, data):
        self.abstract_date = data['abstract_date']
        self.submission_date = data['submission_date']
        self.presentation_date = data['presentation_date']
        self.end_date = data['end_date']

        self.save()

    def actorIsPCMember(self, actor):
        if self.pcmemberin_set.filter(actor_id=actor.id).first() is None:
            return "notPCMember"
        return "Ok"

    def getPCMemberIn(self, actor):
        return self.pcmemberin_set.filter(actor_id=actor.id).first()

    def isChairedBy(self, actor):
        if self is None:
            return "doesNotExist"
        if self.chairedBy.id != actor.id:
            return "notConferenceChair"
        return "Ok"

# this is to automatically add the chair as a pc member
# makes things easier down the road.
@receiver(post_save, sender=Conference)
def _post_save_conference_handler(sender, **kwargs):
    if kwargs['created']:
        conf = kwargs['instance']
        PcMemberIn(description = "Created the conference.", conference = conf, actor = conf.chairedBy).save()

class Submission(models.Model):
    title = models.CharField(max_length = 128)
    abstract = models.CharField(max_length = 2550)
    full_paper = models.CharField(max_length=25500, null=True)
    meta_info = models.CharField(max_length=10000, null=True)
    submitter = models.ForeignKey(Actor, on_delete = models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete = models.CASCADE)

    def actorIsSubmissionAuthor(self, actor):
        if self is None:
            return "doesNotExist"
        if self.submitter.id == actor.id:
            return "actorIsSubmissionAuthor"
        return "Ok"

    def updateInfo(self, data):
        self.title = data['title']
        self.abstract = data['abstract']
        self.full_paper = data['full_paper']
        self.meta_info = data['meta_info']
        self.save()

class BiddingValues:
    DEFAULT = 1
    E = 'Want to Evaluate'
    N = 'Neutral'
    R = 'Refuse to Evaluate'
    CHOICES = (
        (0, 'Want to Evaluate'),
        (1, 'Neutral'),
        (2, 'Refuse to Evaluate'),
    )

class GradingValues:
    DEFAULT = 0
    N  = 'Not Graded'
    SA = 'Strong Accept'
    A  = 'Accept'
    WA = 'Weak Accept'
    B  = 'Borderline'
    WR = 'Weak Reject'
    R  = 'Reject'
    SR = 'Strong Reject'
    CHOICES = (
         (0, 'Not Graded'),
         (1, 'Strong Accept'),
         (2, 'Accept'),
         (3, 'Weak Accept'),
         (4, 'Borderline'),
         (5, 'Weak Reject'),
         (6, 'Reject'),
         (7, 'Strong Reject'),
    )

class PcMemberIn(models.Model):
    description = models.CharField(max_length=1024)
    actor = models.ForeignKey(Actor, on_delete = models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete = models.CASCADE)

    def biddingValueFor(self, submission_id):
        bid = self.bidding_set.filter(id = submission_id).first()

        if bid is None:
            return BiddingValues.N

        return bid.getBid()

class Bidding(models.Model):
    submission = models.ForeignKey(Submission, on_delete = models.CASCADE)
    pcmember = models.ForeignKey(PcMemberIn, on_delete = models.CASCADE)
    bid = models.PositiveSmallIntegerField(default = 1, choices = BiddingValues.CHOICES)

    def getBid(self):
        for x in BiddingValues.CHOICES:
            if self.bid == x[0]:
                return x[1]

class SubmissionRemark(models.Model):
    submission = models.ForeignKey(Submission, on_delete = models.CASCADE)
    pcmember = models.ForeignKey(PcMemberIn, on_delete = models.CASCADE)
    content = models.CharField(max_length=1024)

class ReviewAssignment(models.Model):
    submission = models.ForeignKey(Submission, on_delete = models.CASCADE)
    pcmember = models.ForeignKey(PcMemberIn, on_delete = models.CASCADE)
    grade = models.PositiveSmallIntegerField(default = 1, choices = GradingValues.CHOICES)

    def getGrade(self):
        for x in GradingValues.CHOICES:
            if self.grade == x[0]:
                return x[1]

class EvaluationResult(models.Model):
    grade = models.PositiveSmallIntegerField(default = 1, choices = GradingValues.CHOICES)
    submission = models.OneToOneField(Submission, on_delete = models.CASCADE)

    def getGrade(self):
        for x in GradingValues.CHOICES:
            if self.grade == x[0]:
                return x[1]

################################################################################

def loggedActor(view):
    return Actor.objects.get(pk=view.request.user.id)

