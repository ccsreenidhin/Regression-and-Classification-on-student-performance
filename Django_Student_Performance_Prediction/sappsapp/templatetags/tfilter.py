from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.filter
def get_item(dictionary, key):
    u = User.objects.get(pk=key)
    return u.username
