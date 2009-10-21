import datetime

from django.conf import settings
from django.db import models
from django.db.models import signals

from django.contrib.auth.models import User

from friends.managers import FriendshipManager, FriendshipInvitationManager


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None


class Friendship(models.Model):
    """
    A friendship is a bi-directional association between two users who
    have both agreed to the association.
    """
    
    to_user = models.ForeignKey(User, related_name="friends")
    from_user = models.ForeignKey(User, related_name="_unused_")
    # @@@ relationship types
    added = models.DateField(default=datetime.date.today)
    
    objects = FriendshipManager()
    
    class Meta:
        unique_together = (('to_user', 'from_user'),)


def friend_set_for(user):
    return set([obj["friend"] for obj in Friendship.objects.friends_for_user(user)])


INVITE_STATUS = (
    (1, "Created"),
    (2, "Sent"),
    (3, "Failed"),
    (4, "Expired"),
    (5, "Accepted"),
    (6, "Declined"),
    (7, "Deleted")
)


class FriendshipInvitation(models.Model):
    """
    A frienship invite is an invitation from one user to another to be
    associated as friends.
    """
    
    from_user = models.ForeignKey(User, related_name="invitations_from")
    to_user = models.ForeignKey(User, related_name="invitations_to")
    message = models.TextField()
    sent = models.DateField(default=datetime.date.today)
    status = models.IntegerField(choices=INVITE_STATUS)
    
    objects = FriendshipInvitationManager()
    
    def accept(self):
        if not Friendship.objects.are_friends(self.to_user, self.from_user):
            friendship = Friendship(to_user=self.to_user, from_user=self.from_user)
            friendship.save()
            self.status = "5"
            self.save()
            if notification:
                notification.send([self.from_user], "friends_accept", {"invitation": self})
                notification.send([self.to_user], "friends_accept_sent", {"invitation": self})
                for user in friend_set_for(self.to_user) | friend_set_for(self.from_user):
                    if user != self.to_user and user != self.from_user:
                        notification.send([user], "friends_otherconnect", {
                            "invitation": self,
                            "to_user": self.to_user
                        })
    
    def decline(self):
        if not Friendship.objects.are_friends(self.to_user, self.from_user):
            self.status = "6"
            self.save()


class FriendshipInvitationHistory(models.Model):
    """
    History for friendship invitations
    """
    
    from_user = models.ForeignKey(User, related_name="invitations_from_history")
    to_user = models.ForeignKey(User, related_name="invitations_to_history")
    message = models.TextField()
    sent = models.DateField(default=datetime.date.today)
    status = models.CharField(max_length=1, choices=INVITE_STATUS)


def delete_friendship(sender, instance, **kwargs):
    friendship_invitations = FriendshipInvitation.objects.filter(
        to_user=instance.to_user,
        from_user=instance.from_user
    )
    for friendship_invitation in friendship_invitations:
        if friendship_invitation.status != "8":
            friendship_invitation.status = "8"
            friendship_invitation.save()


signals.pre_delete.connect(delete_friendship, sender=Friendship)


# moves existing friendship invitation from user to user to FriendshipInvitationHistory before saving new invitation
def friendship_invitation(sender, instance, **kwargs):
    friendship_invitations = FriendshipInvitation.objects.filter(
        to_user=instance.to_user,
        from_user=instance.from_user
    )
    for friendship_invitation in friendship_invitations:
        FriendshipInvitationHistory.objects.create(
                from_user=friendship_invitation.from_user,
                to_user=friendship_invitation.to_user,
                message=friendship_invitation.message,
                sent=friendship_invitation.sent,
                status=friendship_invitation.status
                )
        friendship_invitation.delete()


signals.pre_save.connect(friendship_invitation, sender=FriendshipInvitation)
