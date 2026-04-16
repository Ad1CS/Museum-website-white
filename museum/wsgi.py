import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'museum.settings')

application = get_wsgi_application()

# Serve Media files via WhiteNoise in production
if not settings.DEBUG:
    application = WhiteNoise(application, root=settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)
