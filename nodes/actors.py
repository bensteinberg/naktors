import pykka
import time
from .models import Node
import logging

logger = logging.getLogger(__name__)


class Aktor(pykka.ThreadingActor):

    def on_receive(self, message):
        if message['sender'] != self.actor_urn:
            logger.info("%s heard %s from %s" % (self.actor_urn[-4:], message['data'], message['sender']))
        
    def on_start(self):
        logger.info("Started actor %s" % (self.actor_urn,))
        
    def yell(self, content):
        logger.info('%s is yelling "%s"' % (self.actor_urn, content))
        message = { 'sender': self.actor_urn, 'data': content }
        pykka.ActorRegistry.broadcast(message)


