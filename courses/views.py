import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import CustomUser, Course, Module, Video
from .forms import CustomUserCreationForm, CourseForm, ModuleForm, VideoForm

# Helper to check if user is admin
def is_admin(user):
    return user.is_authenticated and user.is_staff

# Helper to check if user is validated (or admin)
def is_validated_user(user):
    return user.is_authenticated and (user.is_validated or user.is_staff)

# Helper to convert video URLs to embeds
def get_embed_url(url):
    yt_match = re.search(r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})', url)
    if yt_match:
        return f"https://www.youtube.com/embed/{yt_match.group(1)}"
    vimeo_match = re.search(r'vimeo\.com\/(?:video\/)?([0-9]+)', url)
    if vimeo_match:
        return f"https://player.vimeo.com/video/{vimeo_match.group(1)}"
    return url

# --- AUTHENTICATION VIEWS ---

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Cuenta creada para {user.username}. Estás pendiente de validación por un administrador.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        print("DEBUG: POST Data:", request.POST)
        form = AuthenticationForm(request, data=request.POST)
        print("DEBUG: Form is valid?", form.is_valid())
        if form.is_valid():
            user = form.get_user()
            print("DEBUG: Authenticated User (Form):", user)
            if user.is_staff or user.is_validated:
                auth_login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'registration/pending.html', {'username': user.username})
        else:
            print("DEBUG: Form errors:", form.errors)
            # Prueba de autenticación directa con los mismos datos del POST
            raw_username = request.POST.get('username')
            raw_password = request.POST.get('password')
            direct_user = authenticate(username=raw_username, password=raw_password)
            print(f"DEBUG: Direct Auth test for {raw_username}:", direct_user)
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})



def logout_view(request):
    auth_logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login')

# --- DASHBOARD VIEW (DISTRIBUTION BY ROLE) ---

@login_required
def dashboard_view(request):
    if request.user.is_staff:
        # Admin dashboard data
        pending_users = CustomUser.objects.filter(is_validated=False, is_staff=False)
        active_users = CustomUser.objects.filter(is_validated=True, is_staff=False)
        courses = Course.objects.all()
        return render(request, 'admin/dashboard.html', {
            'pending_users': pending_users,
            'active_users': active_users,
            'courses': courses,
        })
    else:
        # Check validation status for normal users (safety check if accessed directly)
        if not request.user.is_validated:
            auth_logout(request)
            return render(request, 'registration/pending.html', {'username': request.user.username})
        
        courses = Course.objects.all()
        return render(request, 'student/dashboard.html', {'courses': courses})

# --- USER VALIDATION ACTIONS (ADMIN ONLY) ---

@user_passes_test(is_admin)
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_validated = True
    user.save()
    messages.success(request, f"Usuario {user.username} ha sido aprobado.")
    return redirect('dashboard')

@user_passes_test(is_admin)
def suspend_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_validated = False
    user.save()
    messages.warning(request, f"Acceso de {user.username} suspendido.")
    return redirect('dashboard')

# --- COURSE CRUD (ADMIN ONLY) ---

@user_passes_test(is_admin)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Curso '{course.title}' creado con éxito.")
            return redirect('dashboard')
    else:
        form = CourseForm()
    return render(request, 'admin/course_form.html', {'form': form, 'title': 'Crear Curso'})

@user_passes_test(is_admin)
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Curso '{course.title}' actualizado.")
            return redirect('dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'admin/course_form.html', {'form': form, 'title': 'Editar Curso', 'course': course})

@user_passes_test(is_admin)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.warning(request, f"Curso '{title}' eliminado.")
        return redirect('dashboard')
    return render(request, 'admin/confirm_delete.html', {'object': course, 'type': 'Curso', 'back_url': 'dashboard'})

# --- MODULE CRUD (ADMIN ONLY) ---

@user_passes_test(is_admin)
def module_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, f"Módulo '{module.title}' agregado al curso.")
            return redirect('dashboard')
    else:
        form = ModuleForm()
    return render(request, 'admin/module_form.html', {'form': form, 'course': course, 'title': 'Agregar Módulo'})

@user_passes_test(is_admin)
def module_edit(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, f"Módulo '{module.title}' actualizado.")
            return redirect('dashboard')
    else:
        form = ModuleForm(instance=module)
    return render(request, 'admin/module_form.html', {'form': form, 'course': module.course, 'title': 'Editar Módulo', 'module': module})

@user_passes_test(is_admin)
def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        title = module.title
        module.delete()
        messages.warning(request, f"Módulo '{title}' eliminado.")
        return redirect('dashboard')
    return render(request, 'admin/confirm_delete.html', {'object': module, 'type': 'Módulo', 'back_url': 'dashboard'})

# --- VIDEO CRUD (ADMIN ONLY) ---

@user_passes_test(is_admin)
def video_create(request, module_id):
    module = get_object_or_404(Module, pk=module_id)
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video = form.save(commit=False)
            video.module = module
            video.save()
            messages.success(request, f"Video '{video.title}' agregado a {module.title}.")
            return redirect('dashboard')
    else:
        form = VideoForm()
    return render(request, 'admin/video_form.html', {'form': form, 'module': module, 'title': 'Agregar Video'})

@user_passes_test(is_admin)
def video_edit(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, f"Video '{video.title}' actualizado.")
            return redirect('dashboard')
    else:
        form = VideoForm(instance=video)
    return render(request, 'admin/video_form.html', {'form': form, 'module': video.module, 'title': 'Editar Video', 'video': video})

@user_passes_test(is_admin)
def video_delete(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.method == 'POST':
        title = video.title
        video.delete()
        messages.warning(request, f"Video '{title}' eliminado.")
        return redirect('dashboard')
    return render(request, 'admin/confirm_delete.html', {'object': video, 'type': 'Video', 'back_url': 'dashboard'})

# --- STUDENT CONTENT VIEW (VALIDATED USERS ONLY) ---

@user_passes_test(is_validated_user)
def student_course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    # Get all modules for this course
    modules = course.modules.all().prefetch_related('videos')
    
    # Get active video if provided in query string, else default to first video of first module
    active_video = None
    video_id = request.GET.get('video')
    if video_id:
        active_video = get_object_or_404(Video, id=video_id, module__course=course)
    elif modules.exists():
        first_module = modules.first()
        if first_module.videos.exists():
            active_video = first_module.videos.first()
            
    active_embed_url = get_embed_url(active_video.video_url) if active_video else None

    return render(request, 'student/course_view.html', {
        'course': course,
        'modules': modules,
        'active_video': active_video,
        'active_embed_url': active_embed_url,
    })
