from django.urls import path
from . import  views
from .views import home_view, manage_users_view

urlpatterns = [
    path('', home_view, name='home'),
    path('manage-users/', manage_users_view, name='manage_users'),
    path('contests/', views.contest_list, name='contest_list'),
    path('contests-create/', views.create_contest, name='contest_create'),
    path('contests/<int:pk>/edit/', views.edit_contest, name='contest_edit'),
    path('stage-create/<int:contest_id>/', views.create_stage, name='create_stage'),
    path('contest/<int:id>/', views.contest_detail, name='contest_detail'),
    path('stage/edit/<int:id>/', views.stage_edit, name='stage_edit'),
    path('stage-delete/<int:stage_id>/', views.delete_stage, name='stage_delete'),
    path('stage/<int:id>/', views.stage_detail, name='stage_detail'),
    path('stage/<int:stage_id>/criterion/create/', views.create_criterion, name='create_criterion'),
    path('criterion/<int:criterion_id>/delete/', views.delete_criterion, name='delete_criterion'),
    path('stage/<int:stage_id>/submit/', views.submit_work, name='submit_work'),
    path('submission/<int:submission_id>/evaluate/', views.evaluate_submission, name='evaluate_submission'),

    path('expert/contests/', views.expert_contests, name='expert_contests'),
    path('expert/contests/<int:contest_id>/stages/', views.expert_stages, name='expert_stages'),
    path('expert/stages/<int:stage_id>/submissions/', views.expert_submissions, name='expert_submissions'),
    path('submission/<int:submission_id>/evaluate/', views.evaluate_submission, name='evaluate_submission'),

    path('submission/<int:submission_id>/', views.submission_detail_and_evaluate, name='submission_detail'),

    path('award/create/', views.award_create_view, name='award_create'),
    path('award/create/<int:contest_id>/', views.award_create_view, name='award_create_with_contest'),
]
