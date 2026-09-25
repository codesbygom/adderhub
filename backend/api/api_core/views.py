from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, response, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from core.models import Post, Comment
from .serializers import PostSerializer, PostUpdateSerializer, CommentSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class PostViewSet(viewsets.ModelViewSet):
    """Posts. `?user=<uuid>` narrows the list to one user's posts."""
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    parser_classes     = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        qs = Post.objects.select_related('user')
        user_id = self.request.query_params.get('user')
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs.order_by('-creation_time')

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return PostUpdateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False)
    def feed(self, request):
        """Posts from the users you follow, plus your own."""
        qs = Post.objects.filter(
            user__in=list(request.user.follows.values_list('id', flat=True)) + [request.user.id]
        ).select_related('user').order_by('-creation_time')
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return response.Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """POST likes the post, DELETE removes the like."""
        post = self.get_object()
        if request.method == 'POST':
            post.like_post(request.user)
        else:
            post.unlike_post(request.user)
        return response.Response({'is_liked': post.is_liked_by(request.user), 'likes_count': post.get_likes_count()})


class PostCommentListView(generics.ListCreateAPIView):
    serializer_class   = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_post(self):
        return get_object_or_404(Post, pk=self.kwargs['post_pk'])

    def get_queryset(self):
        return Comment.objects.get_post_comments(self.get_post()).select_related('user')

    def perform_create(self, serializer):
        serializer.save(post=self.get_post(), user=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = Comment.objects.select_related('user')
    serializer_class   = CommentSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
