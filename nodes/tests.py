from django.test import TestCase, Client
from django.contrib.auth.models import User
from nodes.models import Node, NodeConnection, NodeClass
#from nodes.actors import Aktor


class NodeTestCase(TestCase):
    def setUp(self):
        Node.objects.create(name="somenode")
        Node.objects.create(name="anothernode")

    def test_node(self):
        mynode = Node.objects.get(name="somenode")
        self.assertEqual(mynode.actor_urn, None)
        self.assertEqual(mynode.started, False)

    def test_connection(self):
        somenode = Node.objects.get(name="somenode")
        anothernode = Node.objects.get(name="anothernode")
        connection = NodeConnection(from_node=somenode, to_node=anothernode)
        connection.save()
        self.assertEqual(connection.from_node, somenode)
        self.assertEqual(connection.to_node, anothernode)

    def test_class(self):
        somenode = Node.objects.get(name="somenode")
        someclass = NodeClass(class_name="someclass")
        someclass.save()
        somenode.node_classes.add(someclass)
        self.assertEqual(somenode.node_classes.count(), 1)


class AppTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'testuser@example.com', 'testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_node_create_start_stop(self):

        # make a new node
        response = self.client.get('/nodes/new/anode')
        self.assertEqual(response.status_code, 200)
        pk = response.json()['pk']
        self.assertEqual(pk, 1)

        # check it
        response = self.client.get('/nodes/%s/' % (pk,))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'anode')
        self.assertEqual(response.json()['actor_urn'], None)
        self.assertEqual(response.json()['started'], False)

        # start it
        response = self.client.get('/nodes/%s/start' % (pk,))
        self.assertEqual(response.status_code, 200)

        # make sure it's started and get its actor URN
        response = self.client.get('/nodes/%s/' % (pk,))
        self.assertEqual(response.json()['started'], True)
        actor_urn = response.json()['actor_urn']

        # compare with list of actors
        response = self.client.get('/actors/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(actor_urn in response.json()['actors'])

        # stop the actor
        response = self.client.get('/nodes/%s/stop' % (pk,))
        self.assertEqual(response.status_code, 200)

        # check the node again
        response = self.client.get('/nodes/%s/' % (pk,))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'anode')
        self.assertEqual(response.json()['actor_urn'], None)
        self.assertEqual(response.json()['started'], False)

    def test_node_stop_all(self):

        # start with no nodes
        response = self.client.get('/nodes/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['nodes']), 0)

        # make new nodes
        pks = []
        for i in ['a', 'b', 'c']:
            response = self.client.get('/nodes/new/node_%s' % (i,))
            self.assertEqual(response.status_code, 200)
            pks.append(response.json()['pk'])

        # check, start, and re-check new nodes
        for pk in pks:
            response = self.client.get('/nodes/%s/' % (pk,))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['actor_urn'], None)
            self.assertEqual(response.json()['started'], False)

            response = self.client.get('/nodes/%s/start' % (pk,))
            self.assertEqual(response.status_code, 200)
            self.assertNotEqual(response.json()['actor_urn'], None)
            self.assertEqual(response.json()['started'], True)

        response = self.client.get('/nodes/all/stop')
        self.assertEqual(response.status_code, 200)

        for pk in pks:
            response = self.client.get('/nodes/%s/' % (pk,))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['actor_urn'], None)
            self.assertEqual(response.json()['started'], False)

        # try the 'all' routes
        response = self.client.get('/nodes/all/start')
        self.assertEqual(response.status_code, 200)
        for pk in pks:
            response = self.client.get('/nodes/%s/' % (pk,))
            self.assertEqual(response.status_code, 200)
            self.assertNotEqual(response.json()['actor_urn'], None)
            self.assertEqual(response.json()['started'], True)
        # try start_all again, for coverage's sake
        response = self.client.get('/nodes/all/start')
        self.assertEqual(response.status_code, 200)
        # and try to start an already-started node
        response = self.client.get('/nodes/1/start')
        self.assertEqual(response.status_code, 200)

        # pause to make and break a connection
        response = self.client.get('/nodes/1/connect/2')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/nodes/1/disconnect/2')
        self.assertEqual(response.status_code, 200)

        # then stop all
        response = self.client.get('/nodes/all/stop')
        self.assertEqual(response.status_code, 200)
        for pk in pks:
            response = self.client.get('/nodes/%s/' % (pk,))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['actor_urn'], None)
            self.assertEqual(response.json()['started'], False)
        # and try to stop an already-stopped node
        response = self.client.get('/nodes/1/stop')
        self.assertEqual(response.status_code, 200)

        # get some 404s
        response = self.client.get('/nodes/99/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/nodes/99/start')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/nodes/99/stop')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/nodes/99/yell/hello')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/nodes/99/connect/100')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/nodes/99/disconnect/100')
        self.assertEqual(response.status_code, 404)
