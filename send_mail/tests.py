from django.test import TestCase
from channels import Channel
from channels.tests import ChannelTestCase

class EmailChannelTests(ChannelTestCase):
    def petition_app(self):
        return
