from django.contrib import admin
from django.utils.html import format_html
from .models import Employee, Attendance, LeaveRequest, Salary, Developer

@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    # Menampilkan kolom di daftar utama
    list_display = ['show_photo', 'name', 'role', 'order', 'is_active']
    
    # Membuat kolom 'order' dan 'is_active' bisa diedit langsung tanpa buka detail
    list_editable = ['order', 'is_active']
    
    # Filter dan pencarian
    list_filter = ['is_active', 'role']
    search_fields = ['name', 'role']
    
    # Method untuk menampilkan foto kecil di daftar admin
    def show_photo(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 50%; object-fit: cover;" />', obj.image.url)
        return "No Photo"
    show_photo.short_description = 'Foto'

    # Pengaturan tampilan form input
    fieldsets = (
        ('Profil Pengembang', {
            'fields': ('name', 'role', 'image')
        }),
        ('Pengaturan Tampilan', {
            'fields': ('order', 'is_active')
        }),
    )

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'position', 'department', 'salary', 'is_active', 'join_date']
    list_filter = ['is_active', 'department', 'position', 'join_date']
    search_fields = ['employee_id', 'user__username', 'user__first_name', 'user__last_name', 'phone']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informasi User', {
            'fields': ('user',)
        }),
        ('Informasi Karyawan', {
            'fields': ('employee_id', 'position', 'department', 'salary', 'join_date', 'photo')
        }),
        ('Kontak', {
            'fields': ('phone', 'address')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'status', 'late_indicator']
    list_filter = ['status', 'date', 'employee__department']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'employee__employee_id']
    date_hierarchy = 'date'
    
    def late_indicator(self, obj):
        if obj.is_late:
            return format_html('<span style="color: red;">⚠ Terlambat</span>')
        return format_html('<span style="color: green;">✓ Tepat Waktu</span>')
    late_indicator.short_description = 'Keterlambatan'

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'duration_days', 'status', 'created_at']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Karyawan', {
            'fields': ('employee',)
        }),
        ('Detail Izin', {
            'fields': ('leave_type', 'start_date', 'end_date', 'reason', 'attachment')
        }),
        ('Status & Persetujuan', {
            'fields': ('status', 'admin_notes', 'approved_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'basic_salary', 'allowance', 'bonus', 'deduction', 'total_salary', 'payment_date']
    list_filter = ['month', 'payment_date']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    date_hierarchy = 'month'
    readonly_fields = ['total_salary', 'created_at']