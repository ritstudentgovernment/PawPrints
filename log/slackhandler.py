from logging import Handler
from pawprints import secrets
from slacker import Slacker

class SlackHandler(Handler, object):
    slack = None

    def __init__(self):
        super(SlackHandler, self).__init__()
        self.slack = Slacker(secrets.SLACK_TOKEN)

    def emit(self, record): 
        self.slack.chat.post_message('#botspam', self.format(record))
