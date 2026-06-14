from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Course, Module, Video

User = get_user_model()

class CourseManagerTests(TestCase):
    def setUp(self):
        # Create a standard test user
        self.user = User.objects.create_user(
            username='teststudent',
            password='testpassword123',
            email='student@example.com'
        )

        # Create an admin/validated user
        self.validated_user = User.objects.create_user(
            username='validatedstudent',
            password='testpassword123',
            email='validated@example.com',
            is_validated=True
        )

        # Create a course, module, and video
        self.course = Course.objects.create(
            title='Curso de Git y GitHub',
            description='Aprende a usar Git y GitHub para control de versiones.'
        )

        self.module = Module.objects.create(
            course=self.course,
            title='Introducción',
            description='Conceptos básicos de Git.',
            order=1
        )

        self.video = Video.objects.create(
            module=self.module,
            title='Primer Commit',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            description='Cómo hacer un primer commit.',
            order=1
        )

    def test_user_creation(self):
        """Test that user can be created with default parameters."""
        user = User.objects.get(username='teststudent')
        self.assertEqual(user.email, 'student@example.com')
        self.assertFalse(user.is_validated)

    def test_validated_user_creation(self):
        """Test that user can be marked as validated."""
        user = User.objects.get(username='validatedstudent')
        self.assertTrue(user.is_validated)

    def test_course_creation_and_string_representation(self):
        """Test Course creation and string representation."""
        course = Course.objects.get(title='Curso de Git y GitHub')
        self.assertEqual(str(course), 'Curso de Git y GitHub')
        self.assertEqual(course.description, 'Aprende a usar Git y GitHub para control de versiones.')

    def test_module_creation_and_string_representation(self):
        """Test Module creation and string representation."""
        module = Module.objects.get(title='Introducción')
        self.assertEqual(str(module), 'Curso de Git y GitHub - Introducción')
        self.assertEqual(module.order, 1)

    def test_video_creation_and_string_representation(self):
        """Test Video creation and string representation."""
        video = Video.objects.get(title='Primer Commit')
        self.assertEqual(str(video), 'Introducción - Primer Commit')
        self.assertEqual(video.video_url, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')

    def test_root_url_redirects(self):
        """Test that accessing the root URL redirects to the dashboard."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)

    def test_login_page_loads(self):
        """Test that login page loads successfully."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_register_page_loads(self):
        """Test that registration page loads successfully."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

