from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register('posts', PostViewSet, basename='api_post')

urlpatterns = [
    path('posts/<uuid:post_pk>/comments/', PostCommentListView.as_view(), name='api_post_comments'),
    path('comments/<uuid:pk>/', CommentDetailView.as_view(), name='api_comment_detail'),
    path('', include(router.urls)),
]
