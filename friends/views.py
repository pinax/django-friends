from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from friends.models import FriendshipInvitation


@login_required
def find_friends(request):
    if request.GET.get("q"):
        users = User.objects.filter(username__icontains=request.GET["q"])
    else:
        users = None
    return render_to_response("friends/find_friends.html", {
        "users": users,
    }, context_instance=RequestContext(request))


@login_required
def respond_to_friendship_invitation(request, invitation_id, redirect_to_view=None):
    inv = get_object_or_404(FriendshipInvitation,
        to_user = request.user,
        pk = invitation_id,
    )
    response = request.GET.get("response", "a")
    if response == "a":
        inv.accept()
    elif response == "d":
        inv.decline()
    else:
        raise ValueError("%s isn't a valid response to a friendship request %s" % response)
    if redirect_to_view is not None:
        return redirect(redirect_to_view)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


# @login_required
# def add_friend(request):
#     if request.method == "POST":
#         form = AddFriendForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse(find_friends))
#     else:
#         form = AddFriendForm()
#     return render_to_response("friends/add_fiend.html", {
#         "form": form,
#     })