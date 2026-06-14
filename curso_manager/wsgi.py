"""
WSGI config for curso_manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curso_manager.settings')

# Run migrations automatically on Vercel/production startup if a database URL is present
if os.getenv('DATABASE_URL'):
    try:
        import django
        django.setup()
        from django.core.management import call_command
        call_command('migrate', interactive=False)
    except Exception as e:
        print("Error running migrations on startup:", e)

application = get_wsgi_application()
app = application
