from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    # Redirección de raíz al dashboard
    path('', lambda request: redirect('dashboard'), name='root'),

    # Autenticación
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Gestión de usuarios
    path('users/<int:user_id>/approve/', views.approve_user, name='approve_user'),
    path('users/<int:user_id>/suspend/', views.suspend_user, name='suspend_user'),

    # CRUD de Cursos
    path('course/new/', views.course_create, name='course_create'),
    path('course/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('course/<int:pk>/delete/', views.course_delete, name='course_delete'),

    # CRUD de Módulos
    path('course/<int:course_id>/module/new/', views.module_create, name='module_create'),
    path('module/<int:pk>/edit/', views.module_edit, name='module_edit'),
    path('module/<int:pk>/delete/', views.module_delete, name='module_delete'),

    # CRUD de Videos
    path('module/<int:module_id>/video/new/', views.video_create, name='video_create'),
    path('video/<int:pk>/edit/', views.video_edit, name='video_edit'),
    path('video/<int:pk>/delete/', views.video_delete, name='video_delete'),

    # Detalle de Curso (Estudiante)
    path('course/<int:pk>/', views.student_course_detail, name='course_detail'),
]
