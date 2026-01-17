from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance/history/', views.attendance_history, name='attendance_history'),
    path('leave/', views.leave_request_view, name='leave_request'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/add-employee/', views.add_employee_view, name='add_employee'), # URL Baru
    path('admin/employees/', views.employee_list, name='employee_list'),
    path('admin/employee/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('admin/leave/<int:leave_id>/<str:action>/', views.manage_leave, name='manage_leave'),
]