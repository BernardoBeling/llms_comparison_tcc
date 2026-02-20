import os
from django.core.asmgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factory_project.settings')

application = get_asgi_application()