"""
file: consumers.py
desc: Implements WebSocket bindings for Django Channels.
auth: Lukas Yelle (@lxy5611)
"""
import json, string
import petitions.views as views
from profile.models import User
from collections import namedtuple
from channels import Channel, Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http


def serialize_petitions(petitions_obj, user=None):
    """
    Helper Function.
    Serializes petitions into JSON format for transmission back to the frontend via websocket.
    :param petitions_obj: Database object of petitions.
    :return: JSON formatted dump of the sent petitions: {"petitions": [ {}, ... ], "map":[ ... ]}.
    """
    # Initialize varriables
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

        if hasattr(user, "profile"):
            profile = user.profile

        petitions.append({
            'title': petition.title,
            'description': json.dumps(petition.description.replace("'", "\'")),
            'signatures': petition.signatures,
            'author': petition.author.first_name + " " + petition.author.last_name,
            'tags': tags,
            'response': json.dumps({
                'author': User.objects.get(username=petition.response.author).profile.full_name,
                'description': petition.response.description,
                'timestamp': petition.response.created_at.strftime("%B %d, %Y")
            }) if petition.response is not None else False,
            'updates': updates,
            'timestamp': petition.created_at.strftime("%B %d, %Y"),
            'expires': petition.expires.strftime("%B %d, %Y"),
            'status': petition.status,
            'in_progress': petition.in_progress,
            'isSigned': profile.petitions_signed.filter(id=petition.id).exists() if hasattr(user, "profile") else False,
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


def send_petitions_individually(message, petitions):
    for petition in petitions:
        petition = [petition]
        petition = serialize_petitions(petition, message.user)
        message.reply_channel.send({
            "text": json.dumps({
                "command": "get",
                "petition": petition
            })
        })


@channel_session_user_from_http
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

    send_petitions_individually(message, petitions)


@channel_session_user
def petitions_disconnect(message):
    """
    Endpoint for the petitions_disconnect route. Fires when web socket connections are dropped.
    :param message: The WS message channel that disconnected.
    :return: None
    """
    Group("petitions").discard(message.reply_channel)


@channel_session_user
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

                    send_petitions_individually(message, petitions)

                    return None

                message.reply_channel.send({
                    "text": "Error. Must send 'sort' parameter"
                })
                return None
            elif data.command == 'get':
                # Parse the Get command. Required data = id.
                # Gets a single petition with a particular id.
                if data.id:
                    petition = [views.get_petition(data.id, message.user)]
                    petition = serialize_petitions(petition, message.user) if petition[0] else False
                    reply = {
                        "command": "get",
                        "petition": petition
                    }

                    message.reply_channel.send({
                        "text": json.dumps(reply)
                    })
                return None
            elif data.command == 'search':
                # Parse the search command. Required query. Optional = filter.
                # Sends the WS a sorted and optionally filtered list of petitions.
                if data.query:
                    petitions = views.sorting_controller("search", data.query)
                    try:
                        petitions = views.filtering_controller(petitions, data.filter)
                    except AttributeError:
                        pass

                    send_petitions_individually(message, petitions)

                    return None
                return None

        message.reply_channel.send({
            "text": "Error must sent a non-empty 'command' parameter"
        })
        return None

    return None
