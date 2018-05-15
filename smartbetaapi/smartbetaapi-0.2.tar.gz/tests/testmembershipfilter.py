import unittest
from smartbeta_api.membershipfilter import MembershipFilter


class TestMembershipFilter(unittest.TestCase):

    def test_membership_filter(self):

        test_filter = MembershipFilter('ATEURC')
        self.assertEqual(test_filter._identifier, 'ATEURC')


if __name__ == '__main__':
    unittest.main()
