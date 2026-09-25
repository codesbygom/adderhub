from django.urls import path

from . import views

app_name = 'panel'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('users/', views.UserListView.as_view(), name='users'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<uuid:pk>/toggle-active/', views.UserToggleActiveView.as_view(), name='user-toggle-active'),
    path('users/<uuid:pk>/toggle-staff/', views.UserToggleStaffView.as_view(), name='user-toggle-staff'),
    path('posts/', views.PostListView.as_view(), name='posts'),
    path('posts/<uuid:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('comments/', views.CommentListView.as_view(), name='comments'),
    path('comments/<uuid:pk>/delete/', views.CommentDeleteView.as_view(), name='comment-delete'),
]
