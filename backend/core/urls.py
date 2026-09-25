from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('post/<slug:pk>',post, name='post'),
    path('like/',like, name='like'),
    path('post/<slug:pk>/delete', deletepost, name='delete'),
    path('post/<uuid:post_id>/comments/', post_comments, name='post_comments'),
    path('comment/<uuid:comment_id>/delete/', delete_comment, name='delete_comment'),
    path('search/', search, name='search'),
]
