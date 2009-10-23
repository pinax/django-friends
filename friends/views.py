from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from friends.models import FriendshipInvitation


@login_required
def find_friends(request):
    if request.method == "POST":
        u = get_object_or_404(User, pk=request.POST["user_id"])
        FriendshipInvitation.create_friendship_request(request.user, u)
        return HttpResponseRedirect(request.path)
    elif request.GET.get("q"):
        friends = User.objects.filter(username__icontains=request.GET["q"])
    else:
        friends = None
    return render_to_response("friends/find_friends.html", {
        "friends": friends,
    }, context_instance=RequestContext(request))
