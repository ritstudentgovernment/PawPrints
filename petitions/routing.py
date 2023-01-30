"""
Author: Peter Zujko (@zujko)
        Lukas Yelle (@lxy5611)
Desc: Implements channels routing for the petitions app.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/$', consumers.PetitionConsumer),
]
