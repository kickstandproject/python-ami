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

from oslo.config import cfg

from ami.openstack.common import log as logging
from ami.openstack.common import test

CONF = cfg.CONF

logging.setup('ami')


class TestCase(test.BaseTestCase):
    """Test case base class for all unit tests."""

    def setUp(self):
        """Run before each method to initialize test environment."""
        super(TestCase, self).setUp()
