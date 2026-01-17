from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime


class Developer(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    image = models.ImageField(upload_to='developers/') # Membutuhkan library Pillow
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='ID Karyawan')
    phone = models.CharField(max_length=15, verbose_name='No. Telepon')
    address = models.TextField(verbose_name='Alamat')
    position = models.CharField(max_length=100, verbose_name='Jabatan')
    department = models.CharField(max_length=100, verbose_name='Departemen', default='General')
    salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Gaji')
    join_date = models.DateField(verbose_name='Tanggal Bergabung')
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True, verbose_name='Foto')
    is_active = models.BooleanField(default=True, verbose_name='Status Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Karyawan'
        verbose_name_plural = 'Karyawan'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Hadir'),
        ('late', 'Terlambat'),
        ('absent', 'Tidak Hadir'),
        ('permission', 'Izin'),
        ('sick', 'Sakit'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now, verbose_name='Tanggal')
    check_in = models.TimeField(null=True, blank=True, verbose_name='Jam Masuk')
    check_out = models.TimeField(null=True, blank=True, verbose_name='Jam Keluar')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present', verbose_name='Status')
    notes = models.TextField(blank=True, verbose_name='Catatan')
    location = models.CharField(max_length=255, blank=True, verbose_name='Lokasi')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Kehadiran'
        verbose_name_plural = 'Kehadiran'
        unique_together = ['employee', 'date']
        ordering = ['-date', '-check_in']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.get_status_display()}"
    
    @property
    def is_late(self):
        if self.check_in:
            work_start = datetime.strptime('08:00', '%H:%M').time()
            return self.check_in > work_start
        return False

class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('sick', 'Sakit'),
        ('annual', 'Cuti Tahunan'),
        ('personal', 'Keperluan Pribadi'),
        ('marriage', 'Pernikahan'),
        ('maternity', 'Melahirkan'),
        ('other', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES, verbose_name='Jenis Izin')
    start_date = models.DateField(verbose_name='Tanggal Mulai')
    end_date = models.DateField(verbose_name='Tanggal Selesai')
    reason = models.TextField(verbose_name='Alasan')
    attachment = models.FileField(upload_to='leave_attachments/', blank=True, null=True, verbose_name='Lampiran')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    admin_notes = models.TextField(blank=True, verbose_name='Catatan Admin')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Permohonan Izin'
        verbose_name_plural = 'Permohonan Izin'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_leave_type_display()} - {self.get_status_display()}"
    
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1

class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_records')
    month = models.DateField(verbose_name='Bulan')
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Gaji Pokok')
    allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Tunjangan')
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Bonus')
    deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Potongan')
    total_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total Gaji')
    payment_date = models.DateField(null=True, blank=True, verbose_name='Tanggal Pembayaran')
    notes = models.TextField(blank=True, verbose_name='Catatan')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Gaji'
        verbose_name_plural = 'Gaji'
        unique_together = ['employee', 'month']
        ordering = ['-month']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.month.strftime('%B %Y')}"
    
    def save(self, *args, **kwargs):
        self.total_salary = self.basic_salary + self.allowance + self.bonus - self.deduction
        super().save(*args, **kwargs)
        