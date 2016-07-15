from django.test import TestCase, Client
from django.contrib.auth.models import User
from nodes.models import Node
#from nodes.actors import Aktor


class NodeTestCase(TestCase):
    def setUp(self):
        Node.objects.create(name="somenode")

    def test_node(self):
        mynode = Node.objects.get(name="somenode")
        self.assertEqual(mynode.actor_urn, None)
        self.assertEqual(mynode.started, False)


class AppTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.client.login(username='john', password='johnpassword')

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
