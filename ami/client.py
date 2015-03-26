# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

import functools
import socket

from tornado import ioloop
from tornado import iostream

from ami.openstack.common import log as logging
from ami.openstack.common import uuidutils

LOG = logging.getLogger(__name__)

AMI_VERSION = 'Asterisk Call Manager/'


class AMIClient(object):

    def __init__(self):
        self.action_callbacks = {}
        self.event_callbacks = {}
        self.stream = None
        self.version = None

    def connect(
            self, hostname, username, password, port=5038, events=True,
            callback=None):
        sock = socket.socket()
        self.stream = iostream.IOStream(sock)
        func = functools.partial(
            self.login, username=username, password=password, events=events,
            callback=callback)
        self.stream.connect((hostname, port), func)

    def login(self, username, password, events=True, callback=None):
        message = {
            'action': 'login',
            'username': username,
            'secret': password,
        }
        if not events:
            message['events'] = 'off'
        self.send_request(message=message, callback=callback)

    def logoff(self, callback=None):
        message = {
            'action': 'logoff',
        }
        self.send_request(message=message, callback=callback)

    def originate(
            self, channel, context, priority, exten, async=False,
            callback=None):
        message = {
            'action': 'originate',
            'async': async,
            'channel': channel,
            'context': context,
            'priority': priority,
            'exten': exten,
        }
        self.send_request(message=message, callback=callback)

    def ping(self, callback=None):
        message = {
            'action': 'ping',
        }
        self.send_request(message=message, callback=callback)

    def register_event(self, name, callback):
        self.event_callbacks[name] = callback

    def send_request(self, message, callback=None):
        if 'actionid' not in message:
            message['actionid'] = uuidutils.generate_uuid()
        if callback:
            self.action_callbacks[message['actionid']] = callback

        LOG.debug(message)

        for key, value in message.items():
            self.stream.write('%s: %s\r\n' % (key.lower(), value))
        self.stream.write('\r\n')
        self._read()

    def unregister_event(self, name):
        del self.event_callbacks[name]

    def _read(self):
        if not self.stream.reading():
            self.stream.read_until('\r\n\r\n', self._handle_read)

    def _parse(self, message):
        result = dict()
        msg = message.strip()
        for line in msg.split('\r\n'):
            if 'Asterisk Call Manager' in line:
                self.version = line[len(AMI_VERSION):]
                continue
            try:
                key, value = line.split(':', 1)
            except Exception:
                # For some reason the header cannot be split.
                continue
            if key.lower() in result:
                result[key.lower()] += ',' + value.strip()
            else:
                result[key.lower()] = value.strip()

        return result

    def _handle_read(self, data):
        message = self._parse(data)
        LOG.debug(message)
        if 'response' in message:
            self._handle_response(message)
        elif 'event' in message:
            self._handle_event(message)
        if not self.stream.closed():
            self._read()

    def _handle_response(self, message):
        func = self.action_callbacks.get(message['actionid'])
        if func:
            ioloop.IOLoop.current().add_callback(func, message)

    def _handle_event(self, message):
        func = self.event_callbacks.get(message['event'])
        if func:
            ioloop.IOLoop.current().add_callback(func, message)
