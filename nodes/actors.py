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
        
    def on_stop(self):
        """Tell Django so we can update the DB"""
        try:
            for node in Node.objects.filter(actor_urn=self.actor_urn):
                logger.info("Stopping actor, updating node %s" % (node.name,))
                node.actor_urn = None
                node.started = False
                node.save()
        except:
            pass

    def yell(self, content):
        logger.info('%s is yelling "%s"' % (self.actor_urn, content))
        message = { 'sender': self.actor_urn, 'data': content }
        pykka.ActorRegistry.broadcast(message)


