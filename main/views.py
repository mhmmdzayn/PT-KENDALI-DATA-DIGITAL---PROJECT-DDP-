from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from employees.models import Developer

def home(request):
    context = {
        'title': 'Home - PT Kendali Data Digital'
    }
    return render(request, 'main/home.html', context)

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('home') 
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Selamat datang, {user.get_full_name() or user.username}!')
                
                if user.is_staff:
                    return redirect('admin_dashboard') 
                
                return redirect('home') 
            else:
                messages.error(request, 'Akun Anda dinonaktifkan.')
        else:
            messages.error(request, 'Username atau password salah! Silakan coba lagi.')
    
    context = {
        'title': 'Login - PT Kendali Data Digital'
    }
    return render(request, 'registration/login.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Anda telah logout.')
    return redirect('login')

def about(request):
    context = {
        'title': 'About Us - PT Kendali Data Digital',
        'project_description': """
            PT Kendali Data Digital adalah platform Manajemen Kepegawaian (SIMPEG) 
            yang dirancang untuk memodernisasi proses administrasi SDM di perusahaan. 
            Aplikasi ini mengintegrasikan pencatatan kehadiran (absensi) berbasis waktu dan lokasi, 
            pengajuan izin/cuti secara digital, serta manajemen data karyawan yang terpusat.
            
            Tujuan utama kami adalah meningkatkan efisiensi operasional, transparansi data, 
            dan memudahkan monitoring kinerja karyawan secara real-time. Dengan antarmuka yang 
            user-friendly, sistem ini dapat digunakan oleh berbagai skala bisnis untuk 
            transformasi digital yang lebih baik.
        """,
        'features': [
            {'icon': 'bi-clock-history', 'title': 'Absensi Real-time', 'desc': 'Pencatatan waktu masuk dan pulang yang akurat.'},
            {'icon': 'bi-people', 'title': 'Manajemen Karyawan', 'desc': 'Database profil karyawan yang lengkap dan aman.'},
            {'icon': 'bi-calendar-check', 'title': 'Izin & Cuti Digital', 'desc': 'Pengajuan dan persetujuan izin tanpa kertas.'},
            {'icon': 'bi-cash-coin', 'title': 'Rekapitulasi Gaji', 'desc': 'Perhitungan gaji dasar dan tunjangan secara transparan.'}
        ]
    }
    return render(request, 'main/about.html', context)

def gallery_view(request):
    team_members = [
        {
            'name': 'Muhammad Bintang Siregar',
            'nim': '0110225058',
            'role': 'Project Manager',
            'image': '/media/employee_photos/foto1.jpg' 
        },
        {
            'name': 'Muhammad Farraz Wibawa',
            'nim': '0110225010',
            'role': 'Backend Developer',
            'image': 'https://ui-avatars.com/api/?name=Nama+2&background=198754&color=fff&size=200'
        },
        {
            'name': 'Muhammad Zein',
            'nim': '0110225114',
            'role': 'Frontend Developer',
            'image': 'https://ui-avatars.com/api/?name=Nama+3&background=dc3545&color=fff&size=200'
        },
        {
            'name': 'Serli Angraini',
            'nim': '0110225125',
            'role': 'Database Administrator',
            'image': 'https://ui-avatars.com/api/?name=Nama+4&background=ffc107&color=000&size=200'
        },
        {
            'name': 'Dimar Renanthera Riyadi',
            'nim': '0110225024',
            'role': 'UI/UX Designer',
            'image': 'https://ui-avatars.com/api/?name=Nama+5&background=0dcaf0&color=000&size=200'
        },
    ]
    
    context = {
        'title': 'Galeri Tim',
        'website_description': 'Kenali tim hebat di balik pengembangan PT Kendali Data Digital.',
        'team_members': team_members 
    }
    return render(request, 'main/gallery.html', context)