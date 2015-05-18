from eduid_am.testing import AMTestCase
from eduid_userdb.data_samples import NEW_BASIC_USER_EXAMPLE as M
from eduid_userdb.exceptions import MultipleUsersReturned, UserDoesNotExist
from bson import ObjectId
import eduid_userdb


class TestTasks(AMTestCase):

    def setUp(self):
        super(TestTasks, self).setUp()

    def test_get_user_by_id(self):
        user = self.userdb.get_user_by_id(M['_id'])
        self.assertEqual(user.mail_addresses.primary.email, M['mail'])
        with self.assertRaises(UserDoesNotExist):
            self.userdb.get_user_by_id('123456789012')

    def test_get_user_by_mail(self):
        user = self.userdb.get_user_by_mail(M['mailAliases'][0]['email'])
        self.assertEqual(user.user_id, M['_id'])

        # Test unverified mail address in mailAliases, should raise UserDoesNotExist
        with self.assertRaises(UserDoesNotExist):
            self.userdb.get_user_by_mail(M['mailAliases'][1]['email'], raise_on_missing=True)

    def test_user_duplication_exception(self):
        user1 = self.userdb.get_user_by_mail(M['mail'])
        user2_doc = user1.to_dict()
        user2_doc['_id'] = ObjectId()  # make up a new unique identifier
        del user2_doc['modified_ts']   # defeat sync-check mechanism
        self.userdb.save(eduid_userdb.User(data=user2_doc))
        with self.assertRaises(MultipleUsersReturned):
            self.userdb.get_user_by_mail(M['mail'])
