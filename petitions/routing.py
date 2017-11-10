"""
Author: Peter Zujko (@zujko)
        Lukas Yelle (@lxy5611)
Desc: Implements channels routing for the petitions app.
"""
from channels.routing import route
from . import consumers

channel_routing = [

    route("websocket.connect", consumers.petitions_connect),
    route("websocket.receive", consumers.petitions_command),
    route("websocket.disconnect", consumers.petitions_disconnect),

]
