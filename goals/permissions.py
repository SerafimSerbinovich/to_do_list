from rest_framework.permissions import IsAuthenticated


class GoalCategoryPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class GoalPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class GoalCommentPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user