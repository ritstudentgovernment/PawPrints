from datetime import timedelta
from profile.models import Notifications, Profile

from django.utils import timezone

import pytest
from channels.testing import WebsocketCommunicator
from petitions.models import Petition, Tag

from .consumers import PetitionConsumer, get_petitions_and_map


class AuthWebsocketCommunicator(WebsocketCommunicator):
    def __init__(self, application, path, headers=None, subprotocols=None, user=None):
        super(AuthWebsocketCommunicator, self).__init__(
            application, path, headers, subprotocols)
        if user is not None:
            self.scope["user"] = user


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_websocket_consumer_failures():
    communicator = WebsocketCommunicator(PetitionConsumer, "/ws/")

    connected, subprotocol = await communicator.connect()

    assert connected
    response = await communicator.receive_json_from()
    assert response is not None

    # Send a totally invalid command
    await communicator.send_json_to({"invalid": "invalid"})
    response = await communicator.receive_json_from()
    assert response == {"text": "Error must sent a non-empty 'command' parameter"}

    # Send list command with no sort field
    await communicator.send_json_to({"command": "list"})
    response = await communicator.receive_json_from()
    assert response == {"text": "Error. Must send 'sort' parameter"}

    # Send paginate command with no sort field
    await communicator.send_json_to({"command": "paginate"})
    response = await communicator.receive_json_from()
    assert response == {"text": "Error. Must send 'sort' parameter"}

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_websocket_consumer_none():
    communicator = WebsocketCommunicator(PetitionConsumer, "/ws/")

    connected, subprotocol = await communicator.connect()

    assert connected
    response = await communicator.receive_json_from()
    assert response is not None

    await communicator.send_json_to({"command": "search"})
    assert await communicator.receive_nothing() is True

    await communicator.send_json_to({"command": "get"})
    assert await communicator.receive_nothing() is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_websocket_consumer_get(django_user_model):
    username = 'abc123'
    email = 'abc123@rit.edu'
    password = '123'
    django_user_model.objects.create(
        username=username, password=password, email=email)

    user = django_user_model.objects.get(username=username)

    Profile.objects.all().delete()
    Profile.objects.create(user=user, full_name=username,
                           notifications=Notifications.objects.create())
    # Remove all petitions
    Petition.objects.all().delete()

    # Create Tag
    tag = Tag(name='TestTag')
    tag.save()

    pet = Petition(title='Test petition',
                   description='This is a test petition',
                   author=user,
                   created_at=timezone.now(),
                   status=0,
                   expires=timezone.now() + timedelta(days=30)
                   )
    pet.save()
    pet.tags.add(tag)
    pet.save()

    communicator = AuthWebsocketCommunicator(
        PetitionConsumer, "/ws/", user=user)

    connected, subprotocol = await communicator.connect()

    assert connected
    response = await communicator.receive_json_from()
    assert response is not None

    await communicator.send_json_to({"command": "get", "id": 45})
    response = await communicator.receive_json_from()
    assert response == {"command": "get", "petition": False}
    """
    dump = get_petitions_and_map([pet], user)
    await communicator.send_json_to({"command": "get", "id": pet.id})

    response = await communicator.receive_json_from()
    assert response == {"command": "get", "petition": dump}
    """
    await communicator.disconnect()
