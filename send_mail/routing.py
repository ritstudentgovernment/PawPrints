from channels.routing import route, route_class
from .consumers import petition_approved

channel_routing = [
        route('petition-approved', petition_approved),
]
