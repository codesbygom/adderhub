from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework import generics, response, status, views

from .serializers import *



class ChangePasswordView(generics.GenericAPIView):
    serializer_class   = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return response.Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)



class UpdateProfileView(generics.UpdateAPIView):
    serializer_class   = UserProfileUpdateSerializer
    permission_classes = (IsAuthenticated,)
    # multipart so profile_img / background_img can be uploaded here too
    parser_classes     = (JSONParser, FormParser, MultiPartParser)

    def get_object(self):
        return self.request.user



class MeView(generics.RetrieveAPIView):
    serializer_class   = UserMeSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user



class UserProfileDetailView(generics.RetrieveAPIView):
    queryset           = User.objects.all()
    serializer_class   = UserProfileSerializer
    permission_classes = (AllowAny,)



class UserProfileListView(generics.ListAPIView):
    """All users; `?search=<text>` filters by username (same lookup as the
    web search page)."""
    serializer_class   = UserProfileSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        query = self.request.query_params.get('search', '').strip()
        if query:
            exclude = self.request.user if self.request.user.is_authenticated else None
            return User.objects.search_users(query, exclude_user=exclude)
        return User.objects.all()



class SuggestedUsersView(generics.ListAPIView):
    serializer_class   = UserProfileSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class   = None

    def get_queryset(self):
        return User.objects.suggest_users(self.request.user)



class FollowersListView(generics.ListAPIView):
    serializer_class   = UserProfileSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return get_object_or_404(User, pk=self.kwargs['pk']).followed_by.all()



class FollowingListView(generics.ListAPIView):
    serializer_class   = UserProfileSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return get_object_or_404(User, pk=self.kwargs['pk']).follows.all()



class FollowView(views.APIView):
    """POST follows the user, DELETE unfollows them."""
    permission_classes = (IsAuthenticated,)

    def _target(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        if target == request.user:
            return None, response.Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        return target, None

    def _result(self, request, target):
        return response.Response({
            'is_following':    request.user.is_following(target),
            'followers_count': target.followers_count,
        })

    def post(self, request, pk):
        target, error = self._target(request, pk)
        if error:
            return error
        request.user.follow(target)
        return self._result(request, target)

    def delete(self, request, pk):
        target, error = self._target(request, pk)
        if error:
            return error
        request.user.unfollow(target)
        return self._result(request, target)



class UserSignUpView(generics.CreateAPIView):
    serializer_class   = UserProfileCreateSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()
