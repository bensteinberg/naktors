from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class NodeClass(models.Model):
    """
    Not sure what node classes are for yet.
    """
    class_name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "node classes"

    def __str__(self):
        return self.class_name


@python_2_unicode_compatible
class Node(models.Model):
    """
    The node is the persistent object; the actor, the instrument of
    concurrency, is ephemeral.
    """
    name = models.CharField(max_length=200)
    actor_urn = models.CharField(max_length=200, null=True, blank=True)
    started = models.BooleanField(default=False)
    node_classes = models.ManyToManyField(NodeClass)

    @classmethod
    def create(cls, name):
        node = cls(name=name)
        return node

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class NodeConnection(models.Model):
    """
    Node connections are intended to be one-way; if you want a two-way
    connection, make one in each direction.
    """
    from_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='from_node')
    to_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='to_node')

    def __str__(self):
        return "%s -> %s" % (self.from_node.name, self.to_node.name)
