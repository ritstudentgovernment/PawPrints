from channels.routing import route
from channels import include

channel_routing = [
    include("petitions.routing.channel_routing"),
]
