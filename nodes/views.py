from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required

from .models import Node, NodeClass, NodeConnection
from .actors import Aktor

import pykka
import sys
import logging


logger = logging.getLogger(__name__)


@login_required
def index(request):
    return JsonResponse({'nodes': [_as_object(this_node)
                                   for this_node
                                   in Node.objects.order_by('pk')]})


@login_required
def node(request, node_id):
    try:
        this_node = Node.objects.get(pk=node_id)
        return JsonResponse(_as_object(this_node))
    except Node.DoesNotExist:
        raise Http404('No such node')


@login_required
def new(request, node_name):
    this_node = Node.create(node_name)
    this_node.save()
    return JsonResponse(_as_object(this_node))


@login_required
def start(request, node_id):
    try:
        this_node = Node.objects.get(pk=node_id)
        if this_node.started and this_node.actor_urn:
            pass
        else:
            logger.info("%s starting an actor..." % (this_node.name,))
            actor_ref = Aktor.start()
            this_node.actor_urn = actor_ref.actor_urn
            this_node.started = True
            this_node.save()
        return JsonResponse(_as_object(this_node))
    except:
        e = sys.exc_info()[0]
        raise Http404('Error: %s' % (e,))


@login_required
def stop(request, node_id):
    try:
        this_node = Node.objects.get(pk=node_id)
    except:
        raise Http404("No such node")
    try:
        actor_ref = pykka.ActorRegistry.get_by_urn(this_node.actor_urn)
        actor_ref.stop()
        logger.info("Stopped actor %s" % (this_node.actor_urn,))
    except:
        pass
    this_node.started = False
    this_node.actor_urn = None
    this_node.save()
    return JsonResponse(_as_object(this_node))


@login_required
def start_all(request):
    for this_node in Node.objects.all():
        if this_node.started and \
           this_node.actor_urn and \
           pykka.ActorRegistry.get_by_urn(this_node.actor_urn):
            pass
        else:
            logger.info("%s starting an actor..." % (this_node.name,))
            actor_ref = Aktor.start()
            this_node.actor_urn = actor_ref.actor_urn
            this_node.started = True
            this_node.save()
    return JsonResponse({'nodes': [_as_object(this_node)
                                   for this_node
                                   in Node.objects.order_by('pk')]})


@login_required
def stop_all(request):
    # don't use pykka.ActorRegistry.stop_all(), since we need to
    # update the nodes -- or I guess we could and do a single query,
    # prob better
    for actor_ref in pykka.ActorRegistry.get_all():
        actor_ref.stop()
    for this_node in Node.objects.all():
        this_node.started = False
        this_node.actor_urn = None
        this_node.save()
    # logger.info("%s stopped actor %s" % (this_node.name, actor_urn,))
    return index(request)


@login_required
def actors(request):
    return JsonResponse({'actors': [actor_ref.actor_urn
                                    for actor_ref
                                    in pykka.ActorRegistry.get_all()]})


@login_required
def connect(request, from_node_id, to_node_id):
    try:
        from_node = Node.objects.get(pk=from_node_id)
        to_node = Node.objects.get(pk=to_node_id)
        node_connection = NodeConnection(from_node=from_node, to_node=to_node)
        node_connection.save()
        return JsonResponse({'connected':
                             {'from': from_node.name, 'to': to_node.name}})
    except:
        e = sys.exc_info()[0]
        raise Http404('Error: %s' % (e,))


@login_required
def disconnect(request, from_node_id, to_node_id):
    try:
        from_node = Node.objects.get(pk=from_node_id)
        to_node = Node.objects.get(pk=to_node_id)
        node_connection = NodeConnection.objects.get(from_node=from_node,
                                                     to_node=to_node)
        node_connection.delete()
        return JsonResponse({'disconnected':
                             {'from': from_node.name,
                              'to': to_node.name}})
    except:
        e = sys.exc_info()[0]
        raise Http404('Error: %s' % (e,))


@login_required
def broadcast(request, content):
    logger.info('Broadcasting "%s"' % (content,))
    message = {'sender': 'someone', 'data': content}
    pykka.ActorRegistry.broadcast(message)
    return JsonResponse(message)


@login_required
def yell(request, node_id, content):
    try:
        this_node = Node.objects.get(pk=node_id)
    except:
        raise Http404("No such node")
    try:
        actor_ref = pykka.ActorRegistry.get_by_urn(this_node.actor_urn)
        actor_ref.proxy().yell(content)
        logging.info("%s yells %s" % (this_node.actor_urn, content))
        return JsonResponse({'actor': this_node.actor_urn, 'yell': content})
    except:
        raise Http404("Node has no actor")


@login_required
def whisper(request, from_node_id, to_node_id, content):
    try:
        from_node = Node.objects.get(pk=from_node_id)
        to_node = Node.objects.get(pk=to_node_id)
    except:
        raise Http404("No such node")
    if from_node.actor_urn:
        message = {'sender': from_node.actor_urn, 'data': content}
    else:
        raise Http404("Sender %s has no actor" % (from_node.name,))
    try:
        actor_ref = pykka.ActorRegistry.get_by_urn(to_node.actor_urn)
        actor_ref.tell(message)
        logging.info("%s whispered %s to %s" %
                     (from_node.actor_urn[-4:],
                      content,
                      to_node.actor_urn[-4:]))
        return JsonResponse({'from': from_node.actor_urn,
                             'to': to_node.actor_urn,
                             'whisper': content})
    except:
        raise Http404("Receiver %s has no actor" % (to_node.name,))


@login_required
def tell_class(request, node_id, class_name, content):
    try:
        from_node = Node.objects.get(pk=node_id)
    except:
        raise Http404("No such node")
    if from_node.actor_urn and \
       pykka.ActorRegistry.get_by_urn(from_node.actor_urn):
        message = {'sender': from_node.actor_urn, 'data': content}
    else:
        raise Http404("Sender %s has no actor" % (from_node.name,))
    try:
        this_class = NodeClass.objects.get(class_name=class_name)
    except:
        raise Http404("No such class")
    to_nodes = []
    for to_node in Node.objects.all():
        if this_class in to_node.node_classes.all():
            actor_ref = pykka.ActorRegistry.get_by_urn(to_node.actor_urn)
            actor_ref.tell(message)
            to_nodes.append(to_node.name)
    return JsonResponse({'from': from_node.name,
                         'to': to_nodes,
                         'told': content})


@login_required
def tell_network(request, node_id, content):
    try:
        from_node = Node.objects.get(pk=node_id)
    except:
        raise Http404("No such node")
    if from_node.actor_urn and \
       pykka.ActorRegistry.get_by_urn(from_node.actor_urn):
        message = {'sender': from_node.actor_urn, 'data': content}
    else:
        raise Http404("Sender %s has no actor" % (from_node.name,))
    to_nodes = []
    for connection in NodeConnection.objects.filter(from_node=from_node):
        to_node = connection.to_node
        actor_ref = pykka.ActorRegistry.get_by_urn(to_node.actor_urn)
        actor_ref.tell(message)
        to_nodes.append(to_node.name)
    return JsonResponse({'from': from_node.name,
                         'to': to_nodes,
                         'told': content})



def _as_object(this_node):
    classes = [node_class.class_name for
               node_class in
               this_node.node_classes.all()]
    return {'pk': this_node.pk,
            'name': this_node.name,
            'actor_urn': this_node.actor_urn,
            'started': this_node.started,
            'classes': classes}
