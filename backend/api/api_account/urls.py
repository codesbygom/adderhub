from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import *


urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('signup/', UserSignUpView.as_view(), name='api_signup'),
    path('me/', MeView.as_view(), name='api_me'),
    path('update/', UpdateProfileView.as_view(), name='api_update'),
    path('changepassword/', ChangePasswordView.as_view(), name='api_change_password'),
    path('suggestions/', SuggestedUsersView.as_view(), name='api_user_suggestions'),
    path('', UserProfileListView.as_view(), name='api_user_list'),
    path('<uuid:pk>/', UserProfileDetailView.as_view(), name='api_user_detail'),
    path('<uuid:pk>/follow/', FollowView.as_view(), name='api_user_follow'),
    path('<uuid:pk>/followers/', FollowersListView.as_view(), name='api_user_followers'),
    path('<uuid:pk>/following/', FollowingListView.as_view(), name='api_user_following'),
]
