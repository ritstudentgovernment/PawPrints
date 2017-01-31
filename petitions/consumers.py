"""
file: consumers.py
desc: Django Channels
auth: Lukas Yelle (@lukasyelle)
"""
from channels import Group


def ws_add(message):
    message.reply_channel.send({"accept": True})
    Group("petition").add(message.reply_channel)

def ws_message(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.

    Group("petition").send({

        "text": "[user] %s" % message.content['text'],

    })

def ws_disconnect(message):
    Group("petition").discard(message.reply_channel)