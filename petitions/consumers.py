"""
file: consumers.py
desc: Implements WebSocket bindings for Django Channels.
auth: Lukas Yelle (@lxy5611)
"""
import json
import string
import petitions.views as views
from collections import namedtuple
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


def serialize_petitions(petitions_obj, user=None):
    """
    Helper Function.
    Serializes petitions into JSON format for transmission back to the frontend via websocket.
    :param petitions_obj: Database object of petitions.
    :return: JSON formatted dump of the sent petitions: {"petitions": [ {}, ... ], "map":[ ... ]}.
    """

    # Initialize variables
    petition_map = {}
    petitions = []

    # Loop over every object in the petitions object passed to the function.
    for x in range(len(petitions_obj)):
        petition = petitions_obj[x]

        tags = []
        all_tags = petition.tags.all()
        for t in all_tags:
            tags.append({
                "name": t.name,
                "id": t.id
            })

        updates = []
        all_updates = petition.updates.all()
        for u in all_updates:
            updates.append({
                "description": u.description,
                "timestamp": u.created_at.strftime("%B %d, %Y")
            })

        profile = user.profile if hasattr(user, "profile") else False

        petitions.append({
            'title': petition.title,
            'description': json.dumps(petition.description.replace("'", "\'")),
            'signatures': petition.signatures,
            'author': petition.author.first_name + " " + petition.author.last_name,
            'tags': tags,
            'response': json.dumps({
                'author': petition.response.author,
                'description': petition.response.description,
                'timestamp': petition.response.created_at.strftime("%B %d, %Y")
            }) if petition.response is not None else False,
            'updates': updates,
            'timestamp': petition.created_at.strftime("%B %d, %Y"),
            'expires': petition.expires.strftime("%B %d, %Y"),
            'status': petition.status,
            'in_progress': petition.in_progress,
            'isSigned': profile.petitions_signed.filter(id=petition.id).exists() if profile is not False else False,
            'deleted': False,
            'id': petition.id
        })
        petition_map[petition.id] = x

    return json.dumps({
        "petitions": petitions,
        "map": petition_map
    })


def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())


def json2obj(data): return json.loads(data, object_hook=_json_object_hook)


def paginate(petitions, page): return petitions[(page-1)*45:page*45]


class PetitionConsumer(WebsocketConsumer):
    def send_petitions_individually(self, petitions):
        for petition in petitions:
            petition = [petition]
            petition = serialize_petitions(petition, self.scope["user"])

            self.send(json.dumps({
                        "command": "get",
                        "petition": petition
                        }
                    )
                )

    def connect(self):
        """
        Endpoint for the petitions_connect route. Fires when web socket(WS) connections are made to the server.
        :param message: The WS message channel that connected.
        :return: None
        """
        self.group_name = "petitions"
        # Add the WS connection to the petitions channels group
        self.channel_layer.group_add(self.group_name, self.channel_name)

        # Default order is 'most recent' query the database for all petitions in that order.
        petitions = paginate(views.sorting_controller("most recent"), 1)
  
        self.accept()

        self.send_petitions_individually(petitions)

    def disconnect(self, close_code):
        """
        Endpoint for the petitions_disconnect route. Fires when web socket connections are dropped.
        """
        self.channel_layer.group_discard(self.group_name, self.channel_name)

    def receive(self, text_data):
        """
        Endpoint for the petitions_command route. Fires when a WS sends a message.
        Handles the parsing of commands from the frontend (an API, of sorts).
        :param text_data: Data sent to the websocket.
        :return: None
        """
        data = json.loads(text_data)
        
        if data != "":
            command = data.get('command', '')
            if command != '':
                if command == 'list':

                    # Parse the List command. Required data = sort. Optional = filter.
                    # Sends the WS a sorted and optionally filtered list of petitions.
                    sort = data.get('sort','')
                    if sort:
                        petitions = views.sorting_controller(sort)
                        if data.get('filter', ''):
                            petitions = views.filtering_controller(petitions, data.get('filter'))

                        self.send_petitions_individually(petitions)

                        return None

                    self.send({"text": "Error. Must send 'sort' parameter"})
                    return None
                elif command == 'get':
                    # Parse the Get command. Required data = id.
                    # Gets a single petition with a particular id.
                    data_id = data.get('id', '')
                    if data_id:
                        petition = [views.get_petition(
                            data_id, self.scope["user"])]
                        petition = serialize_petitions(
                            petition, self.scope["user"]) if petition[0] else False
                        reply = {
                            "command": "get",
                            "petition": petition
                        }
                        print("Sending to channel name %s" % self.channel_name)
                        self.send({"text": json.dumps(reply)})
                    return None
                elif command == 'search':
                    # Parse the search command. Required query. Optional = filter.
                    # Sends the WS a sorted and optionally filtered list of petitions.
                    query = data.get('query', '')
                    if query:
                        petitions = views.sorting_controller("search", query)
                        self.send_petitions_individually(petitions)
                        return None
                    return None
                elif command == 'paginate':
                    # Parse the pageinate command. Required: page, sort. Optional filter.
                    # Sends the WS a sorted and optionally filtered list of petitions between a range.
                    sort = data.get('sort', '')
                    page = data.get('page', '')
                    if sort and page:
                        petitions = views.sorting_controller(sort)
                        if data.get('filter', ''):
                            petitions = views.filtering_controller(petitions, data.get('filter'))
                        petitions = paginate(petitions, page)
                        self.send_petitions_individually(petitions)
                        return None

                    self.send({"text": "Error. Must send 'sort' parameter"})
                    return None
            self.send({"text": "Error must sent a non-empty 'command' parameter"})
            return None
        return None 
