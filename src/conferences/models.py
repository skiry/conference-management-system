from django.db import models
from django.contrib.auth import get_user_model

# This is so that we create a new actor each time a user is saved.
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class Actor(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)

@receiver(post_save, sender=User)
def _post_save_user_handler(sender, **kwargs):
    Actor(user = kwargs['instance']).save() if kwargs['created'] else None

class Conference(models.Model):
    name = models.CharField(max_length = 255, unique = True)
    website = models.CharField(max_length = 255, unique = True)
    info = models.CharField(max_length = 4096)

    startDate = models.DateField()
    abstractDate = models.DateField()
    submissionDate = models.DateField()
    presentationDate = models.DateField()
    endDate = models.DateField()

    chairedBy = models.ForeignKey(Actor, on_delete = models.CASCADE)

# this is to automatically add the chair as a pc member
# makes things easier down the road.
@receiver(post_save, sender=Conference)
def _post_save_conference_handler(sender, **kwargs):
    if kwargs['created']:
        conf = kwargs['instance']
        PcMemberIn(description = "Created the conference.", conference = conf, actor = conf.chairedBy).save()

class Submission(models.Model):
    abstract = models.CharField(max_length = 255)
    fullPaper = models.CharField(max_length = 25500, null = True)
    metaInfo = models.CharField(max_length = 10000, null = True)
    submitter = models.ForeignKey(Actor, on_delete = models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete = models.CASCADE)

class PcMemberIn(models.Model):
    description = models.CharField(max_length=1024)
    actor = models.ForeignKey(Actor, on_delete = models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete = models.CASCADE)

class BiddingValues:
    E = 'Want to Evaluate'
    N = 'Neutral'
    R = 'Refuse to Evaluate'
    CHOICES = (
        (0, 'Want to Evaluate'),
        (1, 'Neutral'),
        (2, 'Refuse to Evaluate'),
    )

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

################################################################################

def loggedActor(view):
    return Actor.objects.get(pk=view.request.user.id)

