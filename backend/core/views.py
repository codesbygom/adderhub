from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .forms import PostUploadForm, SearchForm
from .models import Post, Comment
from account.models import User


def safe_next(request, fallback='/'):
    """The `next` value from the request, but only if it points back into this
    site -- otherwise a crafted link could bounce users to another domain."""
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()},
                                                    require_https=request.is_secure()):
        return next_url
    return fallback


@login_required
def home(request):
    # Posting only ever happens through the sidebar "Upload Post" overlay
    # now (see static/js/index.js's setupPostUploader) -- an AJAX call, not
    # a normal <form> submit -- so this branch always answers in JSON.
    if request.method == 'POST':
        form = PostUploadForm(request.POST, request.FILES)
        if form.is_valid():
            Post.objects.create_post(
                user=request.user,
                image=form.cleaned_data['image'],
                caption=form.cleaned_data['caption']
            )
            return JsonResponse({'ok': True})
        return JsonResponse({'error': form.errors.get_json_data()}, status=400)

    # "Following" shows only people you follow (plus yourself); the default
    # "Explore" view shows everyone's posts.
    tab = 'following' if request.GET.get('tab') == 'following' else 'explore'
    if tab == 'following':
        posts = Post.objects.get_feed_posts(request.user)
    else:
        posts = Post.objects.all().order_by('-creation_time')
    posts = posts.select_related('user')
    posts_with_likes = [(post, post.is_liked_by(request.user)) for post in posts]

    context = {'posts': posts_with_likes, 'tab': tab}
    return render(request, 'core/index.html', context=context)


@login_required
def post(request, pk):
    post = get_object_or_404(Post, id=pk)
    posts_with_likes = [(post, post.is_liked_by(request.user))]
    context = {'posts': posts_with_likes}
    return render(request, 'core/post-detail.html', context=context)


@login_required
@require_POST
def like(request):
    post_id = request.POST.get('post_id')

    if post_id:
        post = get_object_or_404(Post, id=post_id)
        post.toggle_like(request.user)

    return HttpResponseRedirect(safe_next(request))


@login_required
@require_POST
def deletepost(request, pk):
    post = get_object_or_404(Post, id=pk)
    if post.delete_post(request.user):
        messages.success(request, 'Post deleted successfully!')
    else:
        messages.error(request, 'You can only delete your own posts!')

    return redirect('home')


@login_required
def search(request):
    search_form = SearchForm(request.GET)
    users = None
    if search_form.is_valid():
        query = search_form.cleaned_data['search']
        users = User.objects.search_users(query, exclude_user=request.user)

    context = {'query': users if users and users.exists() else None}
    return render(request, 'core/search.html', context=context)


@login_required
def post_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Comment.objects.create_comment(post=post, user=request.user, text=text)
            messages.success(request, 'Comment added!')
            return redirect('post', pk=post_id)

    comments = Comment.objects.get_post_comments(post)
    context = {'post': post, 'comments': comments}
    return render(request, 'core/post-comments.html', context=context)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    if comment.user == request.user:
        comment.delete()
        messages.success(request, 'Comment deleted!')
    else:
        messages.error(request, 'You can only delete your own comments!')
    return redirect('post', pk=post_id)
