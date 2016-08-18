"""
WSGI config for mysite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

os.environ["AWS_ACCESS_KEY_ID"] = 'AKIAIG2S2TXBB4YEHMEA'
os.environ["AWS_SECRET_ACCESS_KEY"] = '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'

application = get_wsgi_application()
