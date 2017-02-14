from channels.routing import route, route_class
from .consumers import *

channel_routing = [
        route('petition-approved', petition_approved),
        route('petition-update', petition_update),
        route('petition-reached', petition_reached),
]
