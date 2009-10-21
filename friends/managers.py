from django.conf import settings
from django.db import models
from django.db.models import Q


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None


class FriendshipManager(models.Manager):
    def friends_for_user(self, user):
        friends = []
        for friendship in self.filter(from_user=user).select_related(depth=1):
            friends.append({"friend": friendship.to_user, "friendship": friendship})
        for friendship in self.filter(to_user=user).select_related(depth=1):
            friends.append({"friend": friendship.from_user, "friendship": friendship})
        return friends
    
    def are_friends(self, user1, user2):
        return self.filter(
            Q(from_user=user1, to_user=user2) |
            Q(from_user=user2, to_user=user1)
        ).count() > 0
    
    def remove(self, user1, user2):
        if self.filter(from_user=user1, to_user=user2):
            friendship = self.filter(from_user=user1, to_user=user2)
        elif self.filter(from_user=user2, to_user=user1):
            friendship = self.filter(from_user=user2, to_user=user1)
        friendship.delete()


class FriendshipInvitationManager(models.Manager):
    def invitations(self, *args, **kwargs):
        return self.filter(*args, **kwargs).exclude(status__in=[6, 8])
    
    def create_frienship_request(self, from_user, to_user, msg=None):
        inv = self.create(from_usre=from_user, to_user=to_user,
            message=msg or "", status=2)
        if notification:
            notification.send([to_user], "friends_invite", {"invitation": inv})
            notification.send([from_user], "friends_invite_sent", {"invitation": inv})
        return inv
    
    def invitation_status(self, user1, user2):
        invs = self.filter(
            Q(from_user=user1, to_user=user2) | 
            Q(from_user=user2, to_user=user1)
        )
        if not invs:
            return None
        return max(inv.status for inv in invs)
