from core.models import User
from core.serializers import ProfileSerializer
from django.db import transaction
from goals.models import GoalCategory, GoalComment, Goal, Board, BoardParticipant
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')
        fields = '__all__'


class ParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=BoardParticipant.editable_roles)
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardWithParticipantsSerializer(BoardSerializer):
    participants = ParticipantSerializer(many=True)

    def update(self, instance, validated_data):
        request_user = self.context['request'].user

        with transaction.atomic():
            BoardParticipant.objects.filter(board=instance).exclude(user=request_user).delete()
            participants = [
                BoardParticipant(user=participant['user'], role=participant['role'], board=instance)
                for participant in validated_data.get('participants', [])
            ]
            BoardParticipant.objects.bulk_create(participants, ignore_conflicts=True)

            if title := validated_data.get('title'):
                instance.title = title

            instance.save()

        return instance


class GoalCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_board(self, board):
        if board.is_deleted:
            raise ValidationError('Board not exists')

        if not BoardParticipant.objects.filter(
            board_id=board.id,
            user__id=self.context['request'].user.id,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ).exists():
            raise PermissionDenied

        return board


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

    def validate_category(self, category):
        if category.is_deleted:
            raise ValidationError('Category not exists')

        if not BoardParticipant.objects.filter(
                board_id=category.board_id,
                user__id=self.context['request'].user.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ).exists():
            raise PermissionDenied

        return category


class GoalAndUserSerializer(GoalSerializer):
    user = ProfileSerializer(read_only=True)


class GoalCommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_goal(self, goal):
        if goal.status == Goal.Status.archived:
            raise ValidationError('Goal not exists')

        if not BoardParticipant.objects.filter(
                board_id=goal.category.board_id,
                user__id=self.context['request'].user.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ).exists():
            raise PermissionDenied

        return goal


class GoalCommentAndUserSerializer(GoalCommentSerializer):
    user = ProfileSerializer(read_only=True)
    goals = serializers.PrimaryKeyRelatedField(read_only=True)
