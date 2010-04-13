from django.contrib import admin

from friends.models import Friendship, FriendshipInvitation, FriendshipInvitationHistory


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ["id", "from_user", "to_user", "added"]


class FriendshipInvitationAdmin(admin.ModelAdmin):
    list_display = ["id", "from_user", "to_user", "sent", "status"]


class FriendshipInvitationHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "from_user", "to_user", "sent", "status"]


admin.site.register(Friendship, FriendshipAdmin)
admin.site.register(FriendshipInvitation, FriendshipInvitationAdmin)
admin.site.register(FriendshipInvitationHistory, FriendshipInvitationHistoryAdmin)