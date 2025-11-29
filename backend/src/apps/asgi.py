"""
ASGI config for web-ssh project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings.dev')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),            # HTTP 走 Django
    "websocket": AuthMiddlewareStack(        # WebSocket 走 Channels
        URLRouter(websocket_urlpatterns)
    ),
})
