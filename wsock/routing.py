# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/channel/(?P<channel_id>\w+)$", consumers.Consumer.as_asgi()),
]
