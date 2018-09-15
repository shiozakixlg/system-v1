import os
import sys

sys.path.append("/var/www/yqapi")
sys.path.append("/var/www/yqapi/yqapi")
print sys.path
os.environ['DJANGO_SETTINGS_MODULE'] = 'yqapi.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
