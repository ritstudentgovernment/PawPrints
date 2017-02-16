"""
Author: Peter Zujko (@zujko)
        Lukas Yelle (@lxy5611)
Desc: Implements channels routing for the whole pawprints app.
"""
from channels.routing import route
from channels import include
from send_mail.routing import channel_routing

channel_routing = [
    include("petitions.routing.channel_routing"),
    include("send_mail.routing.channel_routing"),
]
