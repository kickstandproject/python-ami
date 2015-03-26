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

import mock

from ami import client
from ami import test


class TestCase(test.TestCase):
    """Test cases for Services."""

    def setUp(self):
        super(TestCase, self).setUp()
        self.client = client.AMIClient()

    @mock.patch.object(client.AMIClient, 'send_request')
    def test_login(self, mock_send_request):
        self.client.login(username='guest', password='guest')
        mock_send_request.assert_called_with(
            callback=None,
            message={'action': 'login', 'username': 'guest', 'secret':
                     'guest'})

    @mock.patch.object(client.AMIClient, 'send_request')
    def test_login_without_events(self, mock_send_request):
        self.client.login(username='guest', password='guest', events=False)
        mock_send_request.assert_called_with(
            callback=None,
            message={'action': 'login', 'username': 'guest', 'secret':
                     'guest', 'events': 'off'})

    @mock.patch.object(client.AMIClient, 'send_request')
    def test_logoff(self, mock_send_request):
        self.client.logoff()
        mock_send_request.assert_called_with(
            callback=None, message={'action': 'logoff'})

    @mock.patch.object(client.AMIClient, 'send_request')
    def test_originate(self, mock_send_request):
        self.client.originate(
            channel='SIP/foo', context='default', priority='1', exten='s')
        mock_send_request.assert_called_with(
            callback=None, message={'action': 'originate', 'priority': '1',
                                    'context': 'default', 'channel': 'SIP/foo',
                                    'exten': 's'})

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

    def test_parse_corrupt(self):
        json = {
            'channel': 'Local/2612@QueueMemberConnector2-b7b0;1',
            'event': 'AgentComplete',
            'holdtime': '369',
            'member': 'Local/2612@QueueMemberConnector2/n',
            'privilege': 'agent,all',
            'queue': 'HelpDesk',
            'reason': 'caller',
            'talktime': '313',
            'timestamp': '1407164168.288160',
            'uniqueid': '1407163485.28592',
            'variable': 'QUEUESRVLEVELPERF=68.9'
        }
        message = "Event: AgentComplete\r\n" \
            "Privilege: agent,all\r\n" \
            "Timestamp: 1407164168.288160\r\n" \
            "Queue: HelpDesk\r\n" \
            "Uniqueid: 1407163485.28592\r\n" \
            "Channel: Local/2612@QueueMemberConnector2-b7b0;1\r\n" \
            "Member: Local/2612@QueueMemberConnector2/n\r\n" \
            "HoldTime: 369\r\n" \
            "TalkTime: 313\r\n" \
            "Reason: caller\r\n" \
            "Variable: QUEUESRVLEVELPERF=68.9\r\n" \
            "V\r\n\r\n"

        res = self.client._parse(message=message)
        self.assertEqual(res, json)

    def test_parse_semicolon(self):
        json = {
            'channel': 'SIP/pbx-01-prod-00000017',
            'event': 'VarSet',
            'privilege': 'dialplan,all',
            'timestamp': '1402079382.726195',
            'uniqueid': '1402079382.23',
            'value': 'sip:213@10.182.21.208:5060',
            'variable': 'SIPURI'
        }
        message = "Event: VarSet\r\n" \
            "Privilege: dialplan,all\r\n" \
            "Timestamp: 1402079382.726195\r\n" \
            "Channel: SIP/pbx-01-prod-00000017\r\n" \
            "Variable: SIPURI\r\n" \
            "Value: sip:213@10.182.21.208:5060\r\n" \
            "Uniqueid: 1402079382.23\r\n\r\n"

        res = self.client._parse(message=message)
        self.assertEqual(res, json)

    def test_parse_agent_called_event(self):
        json = {
            'agentcalled': 'Local/s@default',
            'agentname': '101',
            'calleridname': 'unknown',
            'calleridnum': '101',
            'channelcalling': 'SIP/pbx-0000002c',
            'connectedlinename': 'Paul Belanger',
            'connectedlinenum': '213',
            'context': 'queue',
            'destinationchannel': 'Local/s@default-21e2;1',
            'event': 'AgentCalled',
            'extension': '101',
            'priority': '4',
            'privilege': 'agent,all',
            'queue': 'support',
            'timestamp': '1402425995.139353',
            'uniqueid': '1402425726.166',
            'variable': ('QUEUE_CONTEXT=queue,SIPDOMAIN=example.org,'
                         'SIPURI=sip:213@example.org:5060'),
        }
        message = "Event: AgentCalled\r\n" \
            "Privilege: agent,all\r\n" \
            "Timestamp: 1402425995.139353\r\n" \
            "Queue: support\r\n" \
            "AgentCalled: Local/s@default\r\n" \
            "AgentName: 101\r\n" \
            "ChannelCalling: SIP/pbx-0000002c\r\n" \
            "DestinationChannel: Local/s@default-21e2;1\r\n" \
            "CallerIDNum: 101\r\n" \
            "CallerIDName: unknown\r\n" \
            "ConnectedLineNum: 213\r\n" \
            "ConnectedLineName: Paul Belanger\r\n" \
            "Context: queue\r\n" \
            "Extension: 101\r\n" \
            "Priority: 4\r\n" \
            "Uniqueid: 1402425726.166\r\n" \
            "Variable: QUEUE_CONTEXT=queue\r\n" \
            "Variable: SIPDOMAIN=example.org\r\n" \
            "Variable: SIPURI=sip:213@example.org:5060\r\n\r\n"

        res = self.client._parse(message=message)
        self.assertEqual(res, json)

    @mock.patch.object(client.AMIClient, 'send_request')
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
