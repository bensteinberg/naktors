import pykka
import logging

logger = logging.getLogger(__name__)


class Aktor(pykka.ThreadingActor):

    def on_receive(self, message):
        sender = message.get('sender', None)
        data = message.get('data', None)
        if sender != self.actor_urn:
            logger.info("%s heard %s from %s" %
                        (self.actor_urn[-4:], data, sender))

    def on_start(self):
        logger.info("Started actor %s" % (self.actor_urn,))

    def yell(self, content):
        logger.info('%s is yelling "%s"' % (self.actor_urn, content))
        message = {'sender': self.actor_urn, 'data': content}
        pykka.ActorRegistry.broadcast(message)
