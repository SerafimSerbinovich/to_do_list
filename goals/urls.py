from django.urls import path
from goals.apps import GoalsConfig
from goals.views.categories import CategoryCreateView, CategoryListView, CategoryDetailView
from goals.views.goals import GoalCreateView, GoalListView, GoalDetailView
from goals.views.comments import GoalCommentCreateView, GoalCommentListView, GoalCommentDetailView
app_name = GoalsConfig.name

urlpatterns = [
    # Categories
    path('goal_category/create', CategoryCreateView.as_view(), name='create-category'),
    path('goal_category/list', CategoryListView.as_view(), name='list-categories'),
    path('goal_category/<int:pk>', CategoryDetailView.as_view(), name='category-detail'),
    # Goals
    path('goal/create', GoalCreateView.as_view(), name='create-goal'),
    path('goal/list', GoalListView.as_view(), name='list-goals'),
    path('goal/<int:pk>', GoalDetailView.as_view(), name='goal-detail'),
    # Comments
    path('goal_comment/create', GoalCommentCreateView.as_view(), name='create-comment'),
    path('goal_comment/list', GoalCommentListView.as_view(), name='list-comments'),
    path('goal_comment/<int:pk>', GoalCommentDetailView.as_view(), name='comment-detail')
]