from django.urls import re_path
from utils.ssh import SSHConsumer

websocket_urlpatterns = [
    re_path(r'ws/ssh/(?P<host_id>\d+)/$', SSHConsumer.as_asgi()),
]