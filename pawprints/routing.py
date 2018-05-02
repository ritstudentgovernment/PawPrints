"""
Author: Peter Zujko (@zujko)
        Lukas Yelle (@lxy5611)
Desc: Implements channels routing for the whole pawprints app.
"""
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import petitions.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            petitions.routing.websocket_urlpatterns
        )
    ),
})
