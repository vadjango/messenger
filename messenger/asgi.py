"""
ASGI config for messenger project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from rest_framework import routers

from chating import urls
from chating.middlewares import WebsocketJWTAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messenger.settings')

django_asgi_application = get_asgi_application()


application = ProtocolTypeRouter(
    {
        "http": django_asgi_application,
        "websocket": WebsocketJWTAuthMiddleware(URLRouter(urls.websocket_patterns))
    }
)
