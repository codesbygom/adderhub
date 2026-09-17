from cProfile import Profile
from django.contrib import admin
from django.urls import path
from .views import SignUpView, LoginView, ProfileView, SettingsView, LogoutView, PasswordChangeView, follow, upload_image


urlpatterns = [
    path('follow/',follow,name='follow'),
    path('signup/',SignUpView.as_view(),name='signup'),
    path('login/',LoginView.as_view(redirect_authenticated_user=True),name='login'),
    path('profile/<str:username>/',ProfileView.as_view(), name="profile"),
    path('settings/',SettingsView.as_view(),name="settings"),
    path('settings/password/',PasswordChangeView,name="password"),
    path('settings/upload-image/', upload_image, name='upload_image'),
    path('logout/',LogoutView,name='logout'),
]