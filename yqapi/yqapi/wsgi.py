"""
WSGI config for yqapi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append('/usr/lib/python2.7/site-packages')  
sys.path.append('/usr/lib64/python2.7/site-packages')  

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yqapi.settings")

application = get_wsgi_application()
