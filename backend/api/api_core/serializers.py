from rest_framework import serializers
from core.models import Post, Comment
from account.models import User


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_img']


class CommentSerializer(serializers.ModelSerializer):
    user = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'text', 'creation_time']
        read_only_fields = ['id', 'post', 'user', 'creation_time']


class PostSerializer(serializers.ModelSerializer):
    user           = AuthorSerializer(read_only=True)
    likes_count    = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked       = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'image', 'user', 'caption', 'creation_time', 'likes_count', 'comments_count', 'is_liked']
        read_only_fields = ['id', 'user', 'creation_time']

    def get_likes_count(self, obj):
        return obj.get_likes_count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return False
        return obj.is_liked_by(request.user)


class PostUpdateSerializer(PostSerializer):
    """Once posted, only the caption can change -- the image is fixed."""
    class Meta(PostSerializer.Meta):
        read_only_fields = PostSerializer.Meta.read_only_fields + ['image']
