from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Course, Module, Video

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_validated = False  # De forma explícita, empieza desvalidado
        if commit:
            user.save()
        return user

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej. Curso de Django'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Ej. Aprende a crear aplicaciones desde cero...'}),
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej. Módulo 1: Introducción'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Ej. Conceptos básicos del framework...'}),
            'order': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
        }

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_url', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej. Instalación de Python'}),
            'video_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'Ej. https://www.youtube.com/watch?...'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Ej. En este video instalaremos Python...'}),
            'order': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
        }
