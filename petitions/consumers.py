"""
file: consumers.py
desc: Implements WebSocket bindings for Django Channels.
auth: Lukas Yelle (@lxy5611)
      Peter Zujko (pxz3370)
"""
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

import petitions.views as views


def get_petitions_and_map(petitions_obj, user=None):
    """
    Helper Function.
    Gathers and properly formats petitions for transmission back to the frontend via websocket.
    :param petitions_obj: Database object of petitions.
    :return: formatted object of the sent petitions: {"petitions": [ {}, ... ], "map":[ ... ]}.
    """

    # Initialize variables
    petition_map = {}
    petitions = []

    # Loop over every object in the petitions object passed to the function.
    for i, petition in enumerate(petitions_obj):

        tags = []
        all_tags = petition.tags.all()
        for tag in all_tags:
            tags.append({
                "name": tag.name,
                "id": tag.id
            })

        updates = []
        all_updates = petition.updates.all()
        for update in all_updates:
            updates.append({
                "description": update.description,
                "timestamp": update.created_at.strftime("%B %d, %Y")
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
            'isSigned': profile.petitions_signed.filter(id=petition.id).exists() if not isinstance(profile, bool) else False,
            'deleted': False,
            'id': petition.id
        })
        petition_map[petition.id] = i

    return {
        "petitions": petitions,
        "map": petition_map
    }


def paginate(petitions, page):
    """Range of petitions to be displayed on a page."""
    return petitions[(page-1)*45:page*45]


class PetitionConsumer(JsonWebsocketConsumer):
    """Consumer class for the petitions websocket.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = ""

    def send_petitions_individually(self, petitions):
        for petition in petitions:
            petition = [petition]
            petition = get_petitions_and_map(petition, self.scope["user"])

            self.send_json({"command": "get", "petition": json.dumps(petition)})

    def send_petitions(self, petitions, command=None):
        user = self.scope["user"] if 'user' in self.scope else None
        petitions = get_petitions_and_map(petitions, user)
        if command is not None:
            petitions.update({"command": command})
        self.send_json(petitions)

    def connect(self):
        """
        Endpoint for the petitions_connect route. Fires when web socket(WS) connections are made to the server.
        :param message: The WS message channel that connected.
        :return: None
        """
        self.group_name = "petitions"
        # Add the WS connection to the petitions channels group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name)

        # Default order is 'most recent' query the database for all petitions in that order.
        petitions = paginate(views.sorting_controller("most recent"), 1)

        self.accept()

        self.send_petitions(petitions)

    def disconnect(self, *args):
        """
        Endpoint for the petitions_disconnect route. Fires when web socket connections are dropped.
        """
        del args
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name)

    def group_update(self, content):
        self.send_json(content.get('text', ''))

    def receive_json(self, data):
        """
        Endpoint for the petitions_command route. Fires when a WS sends a message.
        Handles the parsing of commands from the frontend (an API, of sorts).
        :param data: Data sent to the websocket.
        :return: None
        """
        if data != "":
            command = data.get('command', '')
            if command != '':
                if command == 'list':

                    # Parse the List command. Required data = sort. Optional = filter.
                    # Sends the WS a sorted and optionally filtered list of petitions.
                    sort = data.get('sort', '')
                    if sort:
                        petitions = views.sorting_controller(sort)
                        if data.get('filter', ''):
                            petitions = views.filtering_controller(
                                petitions, data.get('filter'))

                        self.send_petitions(petitions)

                        return

                    self.send_json(
                        {"text": "Error. Must send 'sort' parameter"})
                    return
                elif command == 'get':
                    # Parse the Get command. Required data = id.
                    # Gets a single petition with a particular id.
                    data_id = data.get('id', '')
                    if data_id:
                        petition = [views.get_petition(
                            data_id, self.scope["user"])]
                        petition = get_petitions_and_map(
                            petition, self.scope["user"]) if petition[0] else False
                        reply = {
                            "command": "get",
                            "petition": petition
                        }
                        self.send_json(reply)
                    return
                elif command == 'all':
                    # Parse the search command. Required query. Optional = filter.
                    # Sends the WS a sorted and optionally filtered list of petitions.
                    petitions = views.sorting_controller("all")
                    if petitions:
                        self.send_petitions(petitions)
                        return
                    return
                elif command == 'search':
                    # Parse the search command. Required query. Optional = filter.
                    # Sends the WS a sorted and optionally filtered list of petitions.
                    query = data.get('query', '')
                    if query:
                        petitions = views.sorting_controller("search", query)
                        self.send_petitions(petitions)
                        return
                    return
                elif command == 'paginate':
                    # Parse the pageinate command. Required: page, sort. Optional filter.
                    # Sends the WS a sorted and optionally filtered list of petitions in a range.
                    sort = data.get('sort', '')
                    page = data.get('page', '')
                    if sort and page:
                        petitions = views.sorting_controller(sort)
                        if data.get('filter', ''):
                            petitions = views.filtering_controller(
                                petitions, data.get('filter'))
                        petitions = paginate(petitions, page)
                        if len(petitions) > 0:
                            self.send_petitions(petitions, 'paginate')
                        return

                    self.send_json(
                        {"text": "Error. Must send 'sort' parameter"})
                    return
            self.send_json({"text": "Error must sent a non-empty 'command' parameter"})
            return
