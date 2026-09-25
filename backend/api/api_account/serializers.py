from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from account.models import User



class ChangePasswordSerializer(serializers.Serializer):
    old_password         = serializers.CharField(write_only=True)
    new_password         = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Invalid password')
        return value

    def validate(self, data):
        user = self.context['request'].user

        # new password should not be the same as old password
        if data['new_password'] == data['old_password']:
            raise serializers.ValidationError({'new_password': 'New password must be different from old password'})

        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({'confirm_new_password': 'The new password and confirmation do not match.'})

        validate_password(data['new_password'], user)
        return data



class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio', 'profile_img', 'background_img']



class UserProfileSerializer(serializers.ModelSerializer):
    posts_count      = serializers.IntegerField(read_only=True)
    followers_count  = serializers.IntegerField(read_only=True)
    followings_count = serializers.IntegerField(read_only=True)
    is_following     = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'bio',
            'profile_img', 'background_img',
            'posts_count', 'followers_count', 'followings_count', 'is_following',
        ]

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return False
        return request.user.is_following(obj)



class UserMeSerializer(UserProfileSerializer):
    """The signed-in user's own profile -- same as the public one plus the
    private fields (email) nobody else should see."""
    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + ['email', 'is_email_verified']



class UserProfileCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        read_only_fields = ['id']

    def validate(self, data):
        validate_password(data['password'], User(username=data.get('username'), email=data.get('email')))
        return data

    def create(self, validated_data):
        # ModelSerializer.create() would store the password as plain text.
        return User.objects.create_user(**validated_data)
