from django.contrib import admin

from .models import Node, NodeClass, NodeConnection

admin.site.register(Node)
admin.site.register(NodeClass)
admin.site.register(NodeConnection)
