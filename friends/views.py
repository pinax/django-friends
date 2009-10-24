from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from friends.models import FriendshipInvitation


@login_required
def find_friends(request):
    if request.GET.get("q"):
        friends = User.objects.filter(username__icontains=request.GET["q"])
    else:
        friends = None
    return render_to_response("friends/find_friends.html", {
        "friends": friends,
    }, context_instance=RequestContext(request))

"""
@login_required
def add_friend(request):
    if request.method == "POST":
        form = AddFriendForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(find_friends))
    else:
        form = AddFriendForm()
    return render_to_response("friends/add_fiend.html", {
        "form": form,
    })
"""
