"""Drop cached per-user data (account/cache.py) whenever it goes stale."""
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from core.models import Post
from .cache import forget_user
from .models import User


@receiver(m2m_changed, sender=User.follows.through)
def follows_changed(sender, instance, action, reverse, pk_set, **kwargs):
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return
    # both the follower's and every followed user's counters moved
    forget_user(instance.pk, *(pk_set or ()))


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
def post_changed(sender, instance, **kwargs):
    forget_user(instance.user_id)
