"""Cached per-user numbers and lists.

Everything goes through django.core.cache.cache, so it works the same on
Redis, the file cache (PythonAnywhere) or LocMem -- see CACHE_BACKEND in
config/settings.py. Keys are dropped by the signal handlers in
account/signals.py the moment the underlying data changes, so the timeouts
below are only a safety net.
"""
from django.core.cache import cache

STATS_TIMEOUT = 60 * 10
SUGGESTIONS_TIMEOUT = 60 * 5


def stats_key(user_id):
    return f'user:{user_id}:stats'


def suggestions_key(user_id):
    return f'user:{user_id}:suggestions'


def get_user_stats(user):
    """{'posts': n, 'followers': n, 'followings': n} for one user."""
    key = stats_key(user.pk)
    stats = cache.get(key)
    if stats is None:
        stats = {
            'posts': user.post_set.count(),
            'followers': user.followed_by.count(),
            'followings': user.follows.count(),
        }
        cache.set(key, stats, STATS_TIMEOUT)
    return stats


def get_suggestions(user, limit=5):
    """The "who to follow" sidebar list, cached per user."""
    key = suggestions_key(user.pk)
    ids = cache.get(key)
    if ids is None:
        from .models import User
        ids = [str(pk) for pk in User.objects.suggest_users(user, limit=limit).values_list('pk', flat=True)]
        cache.set(key, ids, SUGGESTIONS_TIMEOUT)
    from .models import User
    by_id = {str(u.pk): u for u in User.objects.filter(pk__in=ids, is_active=True)}
    return [by_id[pk] for pk in ids if pk in by_id]


def forget_user(*user_ids):
    cache.delete_many([k for uid in user_ids for k in (stats_key(uid), suggestions_key(uid))])
