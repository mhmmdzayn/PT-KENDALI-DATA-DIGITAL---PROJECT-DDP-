from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Q
from .models import Employee, Attendance, LeaveRequest, Salary
from .forms import LeaveRequestForm, AttendanceForm, EmployeeRegistrationForm, EmployeeProfileForm
from django.contrib.auth import logout

# --- VIEWS KARYAWAN (Hanya akses dashboard sendiri) ---

@login_required
def employee_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        # PENTING: Jika data employee tidak ditemukan, Logout paksa agar tidak error/looping
        messages.error(request, "Akun Anda belum terhubung data Karyawan. Silakan hubungi Admin.")
        logout(request) 
        return redirect('login') # Kembali ke login dengan pesan error

    today = timezone.now().date()
    current_month = timezone.now().replace(day=1).date()
    
    attendance_today = Attendance.objects.filter(employee=employee, date=today).first()
    
    # Statistik User
    user_stats = Attendance.objects.filter(employee=employee, date__gte=current_month).aggregate(
        present=Count('id', filter=Q(status='present')),
        late=Count('id', filter=Q(status='late')),
        absent=Count('id', filter=Q(status='absent')),
    )
    
    context = {
        'title': 'Dashboard Karyawan',
        'employee': employee,
        'attendance_today': attendance_today,
        'stats': user_stats,
    }
    return render(request, 'employees/employee_dashboard.html', context)

# ... (Biarkan fungsi mark_attendance, attendance_history, leave_request_view tetap sama) ...
# Copy fungsi attendance dan leave dari file lama Anda di sini
@login_required
def mark_attendance(request):
    # Pastikan pakai kode yang sudah ada di file lama Anda
    # Cuma tambahkan pengecekan staff redirect di awal
    if request.user.is_staff: return redirect('admin_dashboard')
    
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        return redirect('home')

    today = timezone.now().date()
    attendance = Attendance.objects.filter(employee=employee, date=today).first()
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            att = form.save(commit=False)
            att.employee = employee
            att.date = today
            att.save()
            messages.success(request, 'Kehadiran berhasil dicatat!')
            return redirect('employee_dashboard')
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'employees/mark_attendance.html', {'form': form})

@login_required
def attendance_history(request):
    if request.user.is_staff: return redirect('admin_dashboard')
    try:
        employee = request.user.employee
        history = Attendance.objects.filter(employee=employee).order_by('-date')
    except:
        history = []
    return render(request, 'employees/attendance_history.html', {'history': history})

@login_required
def leave_request_view(request):
    if request.user.is_staff: return redirect('admin_dashboard')
    employee = get_object_or_404(Employee, user=request.user)
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, request.FILES)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.save()
            messages.success(request, 'Permohonan izin terkirim.')
            return redirect('employee_dashboard')
    else:
        form = LeaveRequestForm()
    return render(request, 'employees/leave_request.html', {'form': form})


# --- VIEWS ADMIN (Hanya Staff/Admin) ---

@staff_member_required
def admin_dashboard(request):
    today = timezone.now().date()
    current_month = timezone.now().replace(day=1).date()
    
    # Poin 9: Tampilan Data Lengkap
    context = {
        'total_employees': Employee.objects.filter(is_active=True).count(),
        'present_today': Attendance.objects.filter(date=today, status='present').count(),
        'absent_today': Attendance.objects.filter(date=today, status='absent').count(), # Tambahan
        'pending_leaves': LeaveRequest.objects.filter(status='pending').count(),
        # List Karyawan Terbaru
        'recent_employees': Employee.objects.all().order_by('-join_date')[:5],
        # Absensi Terbaru
        'recent_attendance': Attendance.objects.select_related('employee').order_by('-created_at')[:10],
        # Izin Pending
        'leave_requests': LeaveRequest.objects.filter(status='pending').select_related('employee'),
        # Gaji
        'total_salary': Salary.objects.filter(month=current_month).aggregate(total=Sum('total_salary'))['total'] or 0,
        # Statistik Absensi Bulanan Global
        'attendance_stats': Attendance.objects.filter(date__gte=current_month).aggregate(
             present=Count('id', filter=Q(status='present')),
             late=Count('id', filter=Q(status='late')),
             absent=Count('id', filter=Q(status='absent')),
        )
    }
    return render(request, 'employees/admin_dashboard.html', context)

# Poin 8: Fitur Menambahkan Akun Karyawan (Hanya Admin)
@staff_member_required
def add_employee_view(request):
    if request.method == 'POST':
        user_form = EmployeeRegistrationForm(request.POST)
        profile_form = EmployeeProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            # 1. Buat User Login
            user = user_form.save()
            
            # 2. Buat Data Detail Karyawan
            employee = profile_form.save(commit=False)
            employee.user = user
            employee.employee_id = f"EMP{user.id:04d}" # Generate ID otomatis: EMP0001
            employee.department = request.POST.get('department', 'General')
            employee.position = request.POST.get('position', 'Staff')
            employee.salary = request.POST.get('salary', 0)
            employee.join_date = request.POST.get('join_date', timezone.now().date())
            employee.save()
            
            messages.success(request, f'Karyawan {user.get_full_name()} berhasil ditambahkan!')
            return redirect('admin_dashboard')
    else:
        user_form = EmployeeRegistrationForm()
        profile_form = EmployeeProfileForm()
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Tambah Karyawan Baru'
    }
    return render(request, 'employees/add_employee.html', context)

@staff_member_required
def employee_list(request):
    employees = Employee.objects.all()
    # Logika search dan filter seperti di template employee_list.html
    return render(request, 'employees/employee_list.html', {'employees': employees})

@staff_member_required
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    return render(request, 'employees/employee_detail.html', {'employee': employee})

@staff_member_required
def manage_leave(request, leave_id, action):
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    if action == 'approve':
        leave.status = 'approved'
        messages.success(request, 'Izin disetujui.')
    elif action == 'reject':
        leave.status = 'rejected'
        messages.warning(request, 'Izin ditolak.')
        
    leave.approved_by = request.user
    leave.save()
    return redirect('admin_dashboard')