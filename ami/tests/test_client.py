# Copyright (C) 2014 PolyBeacon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from mock import patch

from ami import client
from ami import test


class TestCase(test.TestCase):
    """Test cases for Services."""

    def setUp(self):
        super(TestCase, self).setUp()
        self.client = client.AMIClient()

    @patch.object(client.AMIClient, 'send_request')
    def test_login(self, mock_send_request):
        self.client.login(username='guest', password='guest')
        mock_send_request.assert_called_with(
            callback=None,
            message={'action': 'login', 'username': 'guest', 'secret':
                     'guest'})

    @patch.object(client.AMIClient, 'send_request')
    def test_login_without_events(self, mock_send_request):
        self.client.login(username='guest', password='guest', events=False)
        mock_send_request.assert_called_with(
            callback=None,
            message={'action': 'login', 'username': 'guest', 'secret':
                     'guest', 'events': 'off'})

    @patch.object(client.AMIClient, 'send_request')
    def test_logoff(self, mock_send_request):
        self.client.logoff()
        mock_send_request.assert_called_with(
            callback=None, message={'action': 'logoff'})

    def test_parse_response(self):
        json = {
            'actionid': 'e9dcec01-173f-4402-9964-26bd4d9f8b3d',
            'message': 'Authentication accepted',
            'response': 'Success'
        }
        message = "Asterisk Call Manager/1.1\r\n" \
            "Response: Success\r\n" \
            "ActionID: e9dcec01-173f-4402-9964-26bd4d9f8b3d\r\n" \
            "Message: Authentication accepted\r\n\r\n"

        res = self.client._parse(message=message)
        self.assertEqual(res, json)
        self.assertEqual(self.client.version, '1.1')

    @patch.object(client.AMIClient, 'send_request')
    def test_ping(self, mock_send_request):
        self.client.ping()
        mock_send_request.assert_called_with(
            callback=None, message={'action': 'ping'})

    def test_register_event(self):
        def handler(self):
            pass

        self.client.register_event('Foo', handler)
        self.assertTrue('Foo' in self.client.event_callbacks)
        self.assertFalse('Bar' in self.client.event_callbacks)
        self.client.unregister_event('Foo')
        self.assertFalse('Foo' in self.client.event_callbacks)
