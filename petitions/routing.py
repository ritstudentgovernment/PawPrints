"""
Author: Peter Zujko (@zujko)
        Lukas Yelle (@lxy5611)
Desc: Implements channels routing for the petitions app.
"""
from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    url(r'^ws/$', consumers.PetitionConsumer),
]
