from unittest import TestCase
from aweber_api import AWeberAPI, AWeberCollection, AWeberEntry
from mock_adapter import MockAdapter


class TestAWeberCollection(TestCase):

    def setUp(self):
        self.aweber = AWeberAPI('1', '2')
        self.aweber.adapter = MockAdapter()
        self.lists = self.aweber.load_from_url('/accounts/1/lists')
        self.aweber.adapter.requests = []

    def test_should_be_a_collection(self):
        self.assertTrue(type(self.lists), AWeberCollection)

    def test_should_have_24_lists(self):
        self.assertTrue(len(self.lists), 24)

    def test_should_be_able_get_each_via_offset(self):
        for i in range(0, 23):
            list = self.lists[i]
            self.assertEqual(type(list), AWeberEntry)
            self.assertEqual(list.type, 'list')

    def test_should_be_able_to_iterate_on_collection(self):
        list_number = 0
        for list in self.lists:
            self.assertEqual(type(list), AWeberEntry)
            self.assertEqual(list.type, 'list')
            list_number += 1
        self.assertEqual(list_number, 24)

    def test_should_support_get_by_id(self):
        list = self.lists.get_by_id(303449)
        self.assertEqual(type(list), AWeberEntry)
        self.assertEqual(list.type, 'list')
        self.assertEqual(list.id, 303449)

    def test_should_support_find_method(self):
        base_url = '/accounts/1/lists/303449/subscribers'
        subscriber_collection = self.aweber.load_from_url(base_url)
        self.aweber.adapter.requests = []
        subscribers = subscriber_collection.find(email='joe@example.com')
        request = self.aweber.adapter.requests[0]

        assert subscribers != False
        assert isinstance(subscribers, AWeberCollection)
        assert len(subscribers) == 1
        assert subscribers[0].self_link == \
                'https://api.aweber.com/1.0/accounts/1/lists/303449/subscribers/50205517'
        assert request['url'] == \
            '{0}?ws.op=find&email=joe%40example.com'.format(base_url)

    def test_find_should_handle_errors(self):
        base_url = '/accounts/1/lists/303449/subscribers'
        subscriber_collection = self.aweber.load_from_url(base_url)
        self.aweber.adapter.requests = []
        subscribers = subscriber_collection.find(name='joe')
        request = self.aweber.adapter.requests[0]

        assert subscribers == False
        assert request['url'] == \
            '{0}?ws.op=find&name=joe'.format(base_url)


class TestCreatingCustomFields(TestCase):

    def setUp(self):
        self.aweber = AWeberAPI('1', '2')
        self.aweber.adapter = MockAdapter()
        cf_url = '/accounts/1/lists/303449/custom_fields'
        self.cf = self.aweber.load_from_url(cf_url)

        self.aweber.adapter.requests = []
        self.resp = self.cf.create(name='Wedding Song')
        self.create_req = self.aweber.adapter.requests[0]
        self.get_req = self.aweber.adapter.requests[1]

    def test_returned_true(self):
        self.assertTrue(self.resp)

    def test_should_have_requested_create_with_post(self):
        self.assertEqual(self.create_req['method'], 'POST')

    def test_should_have_requested_create_on_cf(self):
        self.assertEqual(self.create_req['url'] , self.cf.url)

    def test_should_have_requested_move_with_correct_parameters(self):
        expected_params = {'ws.op': 'create', 'name': 'Wedding Song'}
        self.assertEqual(self.create_req['data'], expected_params)

    def test_should_make_two_requests(self):
        self.assertEqual(len(self.aweber.adapter.requests), 2)

    def test_should_refresh_cf_resource(self):
        self.assertEqual(self.get_req['method'], 'GET')
        self.assertEqual(self.get_req['url'] ,
            '/accounts/1/lists/303449/custom_fields/2')
