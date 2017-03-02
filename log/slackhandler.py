from logging import Handler
from pawprints import secrets
from slacker import Slacker

class SlackHandler(Handler, object):
    slack = None

    def __init__(self):
        super(SlackHandler, self).__init__()
        self.slack = Slacker(secrets.SLACK_TOKEN)

    def emit(self, record): 
        message = ''
        if record.levelname == 'CRITICAL':
            message = '<!channel>:fire::fire::fire:\n'+self.format(record)+'\n'+str(record.exc_info)
        elif record.levelname == 'ERROR':
            message = self.format(record) + '\n' + str(record.exc_info)
        self.slack.chat.post_message(secrets.SLACK_CHANNEL, message, as_user=True)
