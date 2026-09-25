from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from account.models import User
from core.models import Comment, Post
from core.views import safe_next

DASHBOARD_CACHE_KEY = 'panel:dashboard-stats'
DASHBOARD_CACHE_SECONDS = 60


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Logged-out visitors go to the login page; logged-in non-staff get a 403."""
    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff


class SearchMixin:
    """Adds the `q` search box value to the template context."""
    def get_query(self):
        return self.request.GET.get('q', '').strip()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.get_query()
        return ctx


def dashboard_stats():
    """The headline numbers, cached for a minute: they are several COUNT(*)s
    over the biggest tables and nobody needs them to the second."""
    stats = cache.get(DASHBOARD_CACHE_KEY)
    if stats is None:
        week_ago = timezone.now() - timedelta(days=7)
        stats = {
            'user_count': User.objects.count(),
            'post_count': Post.objects.count(),
            'comment_count': Comment.objects.count(),
            'like_count': Post.liked_by.through.objects.count(),
            'new_users': User.objects.filter(date_joined__gte=week_ago).count(),
            'new_posts': Post.objects.filter(creation_time__gte=week_ago).count(),
            'blocked_users': User.objects.filter(is_active=False).count(),
        }
        cache.set(DASHBOARD_CACHE_KEY, stats, DASHBOARD_CACHE_SECONDS)
    return stats


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'panel/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(dashboard_stats())
        ctx['top_posters'] = (User.objects.annotate(n_posts=Count('post'))
                              .filter(n_posts__gt=0).order_by('-n_posts')[:5])
        ctx['recent_posts'] = Post.objects.select_related('user').order_by('-creation_time')[:6]
        return ctx


class UserListView(StaffRequiredMixin, SearchMixin, ListView):
    template_name = 'panel/user_list.html'
    context_object_name = 'users'
    paginate_by = 25

    def get_queryset(self):
        qs = User.objects.annotate(n_posts=Count('post', distinct=True),
                                   n_followers=Count('followed_by', distinct=True))
        q = self.get_query()
        if q:
            qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q) |
                           Q(first_name__icontains=q) | Q(last_name__icontains=q))
        status = self.request.GET.get('status')
        if status == 'blocked':
            qs = qs.filter(is_active=False)
        elif status == 'staff':
            qs = qs.filter(is_staff=True)
        return qs.order_by('-date_joined')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status'] = self.request.GET.get('status', '')
        return ctx


class UserDetailView(StaffRequiredMixin, DetailView):
    model = User
    template_name = 'panel/user_detail.html'
    context_object_name = 'member'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['posts'] = Post.objects.get_user_posts(self.object)[:12]
        ctx['comments'] = Comment.objects.get_user_comments(self.object).select_related('post')[:10]
        return ctx


class UserToggleActiveView(StaffRequiredMixin, View):
    """Blocks / unblocks an account. Nobody can block themselves, and only a
    superuser can block another staff member."""
    http_method_names = ['post']

    def post(self, request, pk):
        member = get_object_or_404(User, pk=pk)
        if member == request.user:
            messages.error(request, "You can't block your own account.")
        elif (member.is_staff or member.is_superuser) and not request.user.is_superuser:
            messages.error(request, 'Only a superuser can block staff accounts.')
        else:
            member.is_active = not member.is_active
            member.save(update_fields=['is_active'])
            cache.delete(DASHBOARD_CACHE_KEY)
            messages.success(request, f'@{member.username} {"unblocked" if member.is_active else "blocked"}.')
        return redirect('panel:user-detail', pk=pk)


class UserToggleStaffView(StaffRequiredMixin, View):
    """Grants / revokes panel access. Superusers only, and not on themselves."""
    http_method_names = ['post']

    def post(self, request, pk):
        member = get_object_or_404(User, pk=pk)
        if not request.user.is_superuser:
            messages.error(request, 'Only a superuser can change staff access.')
        elif member == request.user:
            messages.error(request, "You can't change your own staff access.")
        else:
            member.is_staff = not member.is_staff
            member.save(update_fields=['is_staff'])
            messages.success(request, f'@{member.username} is {"now" if member.is_staff else "no longer"} staff.')
        return redirect('panel:user-detail', pk=pk)


class PostListView(StaffRequiredMixin, SearchMixin, ListView):
    template_name = 'panel/post_list.html'
    context_object_name = 'posts'
    paginate_by = 24

    def get_queryset(self):
        qs = Post.objects.select_related('user').annotate(
            n_likes=Count('liked_by', distinct=True), n_comments=Count('comments', distinct=True))
        q = self.get_query()
        if q:
            qs = qs.filter(Q(caption__icontains=q) | Q(user__username__icontains=q))
        return qs.order_by('-creation_time')


class PostDeleteView(StaffRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        cache.delete(DASHBOARD_CACHE_KEY)
        messages.success(request, f"Post by @{post.user.username} deleted.")
        return redirect(safe_next(request, fallback=reverse('panel:posts')))


class CommentListView(StaffRequiredMixin, SearchMixin, ListView):
    template_name = 'panel/comment_list.html'
    context_object_name = 'comments'
    paginate_by = 30

    def get_queryset(self):
        qs = Comment.objects.select_related('user', 'post', 'post__user')
        q = self.get_query()
        if q:
            qs = qs.filter(Q(text__icontains=q) | Q(user__username__icontains=q))
        return qs.order_by('-creation_time')


class CommentDeleteView(StaffRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.delete()
        cache.delete(DASHBOARD_CACHE_KEY)
        messages.success(request, f'Comment by @{comment.user.username} deleted.')
        return redirect('panel:comments')
