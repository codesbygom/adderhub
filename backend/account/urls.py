from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from .views import SignUpView, LoginView, ProfileView, SettingsView, LogoutView, PasswordChangeView, follow, follow_list, upload_image


urlpatterns = [
    path('follow/',follow,name='follow'),
    path('signup/',SignUpView.as_view(),name='signup'),
    path('login/',LoginView.as_view(redirect_authenticated_user=True),name='login'),
    path('profile/<str:username>/',ProfileView.as_view(), name="profile"),
    path('profile/<str:username>/followers/', follow_list, {'kind': 'followers'}, name='followers'),
    path('profile/<str:username>/following/', follow_list, {'kind': 'following'}, name='following'),
    path('settings/',SettingsView.as_view(),name="settings"),
    path('settings/password/',PasswordChangeView,name="password"),
    path('settings/upload-image/', upload_image, name='upload_image'),
    path('logout/',LogoutView,name='logout'),
]