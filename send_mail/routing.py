from channels.routing import route
from .consumers import petition_approved

channel_routing = [
    route('petition_approved', petition_approved),
]
