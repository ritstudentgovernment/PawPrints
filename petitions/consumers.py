"""
file: consumers.py
desc: Implements WebSocket bindings for Django Channels.
auth: Lukas Yelle (@lxy5611)
"""
from channels import Group
from collections import namedtuple
import petitions.views as views
import json, string

def serialize_petitions(petitions_obj):
    """
    Helper Function.
    Serializes petitions into JSON format for transmission back to the frontend via websocket.
    :param petitions_obj: Database object of petitions.
    :return: JSON formatted dump of the sent petitions: {"petitions": [ {}, ... ], "map":[ ... ]}.
    """
    # Initialize varriables
    petition_map = {}
    petitions = []

    # Loop over ever object in the sent petitions object
    for x in range(len(petitions_obj)):
        petition = petitions_obj[x]

        tags = []
        all_tags = petition.tags.all()
        for t in all_tags:
            tags.append({
                "name":t.name,
                "id":t.id
            })

        updates = []
        all_updates = petition.updates.all()
        for u in all_updates:
            updates.append({
                "description":u.description,
                "timestamp":u.created_at
            })

        petitions.append({
            'title': petition.title,
            'description': json.dumps(petition.description.replace("'","\'")),
            'signatures': petition.signatures,
            'author': petition.author.first_name +" "+ petition.author.last_name,
            'tags': tags,
            'response':petition.response,
            'updates':updates,
            'id': petition.id
        })
        petition_map[petition.id] = x

    return json.dumps({
        "petitions":petitions,
        "map":petition_map
    })

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def petitions_connect(message):
    """
    Endpoint for the petitions_connect route. Fires when web socket(WS) connections are made to the server.
    :param message: The WS message channel that connected.
    :return: None
    """
    # Notify the WS that the connection was accepted.
    message.reply_channel.send({"accept": True})

    # Add the WS connection to the petitions channels group
    Group("petitions").add(message.reply_channel)

    # Default order is 'most recent' query the database for all petitions in that order.
    petitions = views.sorting_controller("most recent")

    # Send the user back the JSON serialized petition objects.
    message.reply_channel.send({
        "text": serialize_petitions(petitions)
    })

def petitions_disconnect(message):
    """
    Endpoint for the petitions_disconnect route. Fires when web socket connections are dropped.
    :param message: The WS message channel that disconnected.
    :return: None
    """
    Group("petitions").discard(message.reply_channel)

def petitions_command(message):
    """
    Endpoint for the petitions_command route. Fires when a WS sends a message.
    Handles the parsing of commands from the frontend (an API, of sorts).
    :param message: The WS message sent.
    :return: None
    """

    sent = message.content['text']
    if sent != "":
        data = json2obj(sent)
        if data.command and data.command != '':
            if data.command == 'list':
                # Parse the List command. Required data = sort. Optional = filter.
                # Sends the WS a sorted and optionally filtered list of petitions.
                if data.sort:
                    petitions = views.sorting_controller(data.sort)
                    if data.filter:
                        petitions = views.filtering_controller(petitions, data.filter)
                    message.reply_channel.send({
                        "text": serialize_petitions(petitions)
                    })
                    return None

                message.reply_channel.send({
                    "text": "Error. Must send 'sort' parameter"
                })
                return None

        message.reply_channel.send({
            "text": "Error must sent a non-empty 'command' parameter"
        })
        return None

    return None