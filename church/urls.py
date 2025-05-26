from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.utils.translation import gettext_lazy as _
from .views import download_reports, download_worshipers, add_pastor

app_name = 'church'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='church/auth/password_reset.html',
             email_template_name='church/auth/password_reset_email.html',
             subject_template_name='church/auth/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='church/auth/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='church/auth/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='church/auth/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Main views
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='church/auth/password_change.html',
        success_url='/password-change/done/'
    ), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='church/auth/password_change_done.html'
    ), name='password_change_done'),
    path('set-language/', views.set_language, name='set_language'),
    
    # Admin views
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # Reverend views
    path('pastors/', views.pastor_list, name='pastor_list'),
    path('pastors/create/', views.pastor_create, name='pastor_create'),
    path('pastors/add/', add_pastor, name='add_pastor'),
    path('pastors/<int:pastor_id>/delete/', views.pastor_delete, name='pastor_delete'),
    path('pastors/assign-church/', views.pastor_assign_church, name='pastor_assign_church'),
    path('churches/<int:church_id>/unassign/', views.unassign_pastor, name='unassign_pastor'),
    
    # Pastor views
    path('worshipers/', views.worshiper_list, name='worshiper_list'),
    path('worshipers/create/', views.worshiper_create, name='worshiper_create'),
    path('worshipers/<int:pk>/edit/', views.worshiper_edit, name='worshiper_edit'),
    path('worshipers/<int:pk>/delete/', views.worshiper_delete, name='worshiper_delete'),
    path('worshipers/<int:worshiper_id>/deceased/', views.mark_worshiper_deceased, name='mark_worshiper_deceased'),
    path('worshipers/<int:worshiper_id>/delete/', views.delete_worshiper, name='delete_worshiper'),
    
    
    # Attendance views
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/create/', views.attendance_create, name='attendance_create'),
    path('attendance/<int:pk>/edit/', views.attendance_edit, name='attendance_edit'),
    path('attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
    
    # News views
    path('news/', views.news_list, name='news_list'),
    path('news/create/', views.news_create, name='news_create'),
    path('news/<int:pk>/edit/', views.news_edit, name='news_edit'),
    path('news/<int:pk>/delete/', views.news_delete, name='news_delete'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    
    # Reports
    path('reports/', views.reports_dashboard, name='reports'),
    path('api/attendance-chart/', views.attendance_chart_data, name='attendance_chart_data'),
    path('provinces/create/', views.province_create, name='province_create'),
    path('districts/create/', views.district_create, name='district_create'),
    path('churches/create/', views.church_create, name='church_create'),

    path('main-reverends/create/', views.main_reverend_create, name='main_reverend_create'),
    # path('api/districts/', views.district_list_api, name='district_list_api'),


     # Province URLs
    path('provinces/', views.province_list, name='province_list'),
    path('provinces/create/', views.province_create, name='province_create'),
    path('provinces/<int:pk>/edit/', views.province_edit, name='province_edit'),
    path('provinces/<int:pk>/delete/', views.province_delete, name='province_delete'),
    
    # District URLs
    path('districts/', views.district_list, name='district_list'),
    path('districts/create/', views.district_create, name='district_create'),
    path('districts/<int:pk>/edit/', views.district_edit, name='district_edit'),
    path('districts/<int:pk>/delete/', views.district_delete, name='district_delete'),
     path('api/districts/', views.district_list_api, name='district_list_api'),
    
    # Church URLs
    path('churches/', views.church_list, name='church_list'),
    path('churches/create/', views.church_create, name='church_create'),
    path('churches/<int:pk>/edit/', views.church_edit, name='church_edit'),
    path('churches/<int:pk>/delete/', views.church_delete, name='church_delete'),
    path('churches/<int:church_id>/assign-church/', views.assign_church, name='assign_church'),
    
    path('reports/download/', download_reports, name='download_reports'),
    path('worshipers/download/', download_worshipers, name='download_worshipers'),
    path('reports/', views.reports_dashboard, name='reports'),
    path('search/', views.search, name='search'),
    path('reverend-search/', views.reverend_search, name='reverend_search'),
]