from goals.models import BoardParticipant
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS


class BoardPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        _filters = {'user': request.user, 'board': obj}
        if request.method not in SAFE_METHODS:
            _filters['role'] = BoardParticipant.Role.owner

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalCategoryPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        _filters = {'user': request.user, 'board': obj.board}
        if request.method not in SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        _filters = {'user': request.user, 'board': obj.category.board}
        if request.method not in SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalCommentPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.user