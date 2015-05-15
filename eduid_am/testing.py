#
# Copyright (c) 2013, 2014, 2015 NORDUnet A/S
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.
#     3. Neither the name of the NORDUnet nor the names of its
#        contributors may be used to endorse or promote products derived
#        from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

"""
Code used in unit tests of various eduID applications.
"""

__author__ = 'leifj'

import time
import atexit
import random
import tempfile
import unittest
import subprocess
import pymongo
from datetime import datetime
from copy import deepcopy

from bson import ObjectId

from eduid_userdb.testing import get_two_test_users

from eduid_userdb import UserDB, User
from eduid_userdb.data_samples import NEW_BASIC_USER_EXAMPLE

from eduid_am.celery import celery, get_attribute_manager

import logging
logger = logging.getLogger(__name__)


TEST_SETTINGS = {
            'BROKER_TRANSPORT': 'memory',
            'BROKER_URL': 'memory://',
            'CELERY_EAGER_PROPAGATES_EXCEPTIONS': True,
            'CELERY_ALWAYS_EAGER': True,
            'CELERY_RESULT_BACKEND': "cache",
            'CELERY_CACHE_BACKEND': 'memory',
            'MONGO_URI': self.tmp_db.get_uri(),
            'MONGO_DBNAME': 'eduid_userdb',
        }


class AMTestCase(unittest.TestCase):
    """TestCase with an embedded MongoDB temporary instance.

    Each test runs on a temporary instance of MongoDB. The instance will
    be listen in a random port between 40000 and 5000.

    A test can access the connection using the attribute `conn`.
    A test can access the port using the attribute `port`
    """

    def setUp(self, userdb_use_old_format=False):
        """
        Test case initialization.

        :return:
        """
        super(AMTestCase, self).setUp()

        self.am = get_attribute_manager(celery)

        # Be sure to tell AttributeManager.get_userdb() about the temporary
        # mongodb instance.
        self.am.default_db_uri = self.tmp_db.get_uri()
        self.userdb = self.am.get_userdb('default')

        self.userdb._drop_whole_collection()

        # Set up test users in the MongoDB. Read the users from MockedUserDB, which might
        # be overridden by subclasses.
        for userdoc in get_two_test_users():
            this = deepcopy(userdoc)  # deep-copy to not have side effects between tests
            user = User(data=this)
            self.userdb.save(user, check_sync=False, old_format=userdb_use_old_format)

    def tearDown(self):
        super(AMTestCase, self).tearDown()
        for userdoc in self.amdb._get_all_userdocs():
            assert User(userdoc)
        self.amdb._drop_whole_collection()

    def mongodb_uri(self, dbname=None):
        return self.tmp_db.get_uri(dbname=dbname)

