from django import template

from friends.models import Friendship, FriendshipInvitation, INVITE_STATUS


register = template.Library()


class FriendshipStatusNode(template.Node):
    def __init__(self, user1, user2, varname=None):
        self.user1 = user1
        self.user2 = user2
        self.varname = varname
    
    def render(self, context):
        user1 = self.user1.resolve(context)
        user2 = self.user2.resolve(context)
        if Friendship.objects.are_friends(user1, user2):
            status = "friends"
        else:
            status = FriendshipInvitation.objects.invitation_status(user1, user2)
            if status is not None:
                status = INVITE_STATUS[status-1]
        if self.varname:
            context[self.varname] = status
            return ''
        return status

@register.tag
def friendship_status(parser, token):
    bits = token.split_contents()
    tag_name = bits[0]
    bits = bits[1:]
    if len(bits) == 4:
        if bits[2] != "as":
            raise template.TemplateSyntaxError("This tag should be used like: "
                "{%% %s user1 user2 [as varname] %%}" % tag_name)
        return FriendshipStatusNode(
            parser.compile_filter(bits[0]),
            parser.compile_filter(bits[1]),
            bits[3]
        )
    elif len(bits) == 2:
        return FriendshipStatusNode(
            parser.compile_filter(bits[0]),
            parser.compile_filter(bits[1])
        )
    else:
        raise template.TemplateSyntaxError("This tag should be used like: "
            "{%% %s user1 user2 [as varname] %%}" % tag_name)
