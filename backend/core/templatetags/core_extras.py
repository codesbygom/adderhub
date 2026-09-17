from django import template
from core.forms import SearchForm
from account.models import User
register = template.Library()

@register.simple_tag
def active(request, pattern):
    path = request.path
    if path == pattern:
        return 'active'
    return ''

@register.simple_tag
def suggested_users(user, limit=5):
    return User.objects.suggest_users(user, limit=limit)

# @register.simple_tag
# def searchform():
#     return SearchForm()