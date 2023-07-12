from core.serializers import ProfileSerializer
from goals.models import GoalCategory, GoalComment, Goal
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied


class GoalCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')


class GoalCategoryAndUserSerializer(GoalCategorySerializer):
    user = ProfileSerializer(read_only=True)


class GoalSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, value):
        if value.is_deleted:
            raise NotFound('Category was deleted')
        if self.context['request'].user.id != value.user_id:
            raise PermissionDenied

        return value


class GoalAndUserSerializer(GoalSerializer):
    user = ProfileSerializer(read_only=True)


class GoalCommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_goal(self, value):
        if value.status == Goal.Status.archived:
            raise NotFound('Goal not found')
        if self.context['request'].user.id != value.user_id:
            raise PermissionDenied

        return value


class GoalCommentAndUserSerializer(GoalCommentSerializer):
    user = ProfileSerializer(read_only=True)
    goals = serializers.PrimaryKeyRelatedField(read_only=True)
