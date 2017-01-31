from channels import route_class, route
from petitions.consumers import Demultiplexer, ws_add, ws_disconnect, ws_message
from petitions.models import PetitionBinding

channel_routing = [

    route("websocket.connect", ws_add),
    route("websocket.receive", ws_message),
    route("websocket.disconnect", ws_disconnect),
    route_class(Demultiplexer, path="^/binding/"),

]

"""

User Connects -> Added to group -> When something changes -> Data Binding ->

"""