"""Urls.py"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('manager_dashboard/', views.dashboard, name='manager_dashboard'),

    path('project/<int:project_id>/add_comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    path('dashboard/team_lead/', views.team_lead_dashboard, name='team_lead_dashboard'),
    path('dashboard/employee/', views.employee_dashboard, name='employee_dashboard'),

    path('dashboard/project/create/', views.create_project, name='create_project'),
    path('project/<int:project_id>/', views.project_details, name='project_details'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('project/<int:project_id>/edit_budgeted_resources/', views.edit_budgeted_resources, name='edit_budgeted_resources'),
    
    path('project/<int:project_id>/manage_resources/', views.manage_resources, name='manage_resources'),
    path('resource/<int:resource_id>/edit/', views.edit_employee_resource, name='edit_employee_resource'),
    path('resource/<int:resource_id>/delete/', views.delete_employee_resource, name='delete_employee_resource'),
    path('resource/<int:resource_id>/check_allocation_conflict/', views.check_allocation_conflict, name='check_allocation_conflict'),
    path('resources/overview/', views.resource_allocation_overview, name='resource_allocation_overview'),
    path('project/<int:project_id>/add_employee_resource/', views.add_employee_resource, name='add_employee_resource'),

    path('manager_dashboard/add_employee/', views.add_employee, name='add_employee'),

    path('employee_overview/', views.employee_overview, name='employee_overview'),
    path('employee/<int:employee_id>/edit/', views.edit_employee, name='edit_employee'),
    path('employee/<int:employee_id>/delete/', views.delete_employee, name='delete_employee'),
    path('month_resource_allocation/', views.month_resource_allocation_overview, name='month_resource_allocation_overview'),
    path('employee_management/', views.employee_management, name='employee_management'),
]
