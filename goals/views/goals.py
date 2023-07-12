from django_filters.rest_framework import DjangoFilterBackend
from goals.filter import GoalDateFilter
from goals.models import Goal
from goals.permissions import GoalPermission

from goals.serializers import GoalSerializer, GoalAndUserSerializer
from rest_framework import generics, permissions, filters


class GoalCreateView(generics.CreateAPIView):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]


class GoalListView(generics.ListAPIView):
    serializer_class = GoalAndUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ['title', 'description']
    ordering = ['title']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Goal.objects.select_related('user').filter(
            user=self.request.user,
            category__is_deleted=False
        )


class GoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [GoalPermission]
    serializer_class = GoalAndUserSerializer

    def get_queryset(self):
        return Goal.objects.select_related('user').filter(
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)

    def perform_destroy(self, instance):
        instance.status = Goal.Status.archived
        instance.save()