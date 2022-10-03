import unittest
import gather
from gather import routes


class TestRoutes(unittest.TestCase):
    """testing routes.py"""
    # use python test_routes.py to run tests
    def test_is_admin(self):
        """tesing is_admin function
        should recognise admin or mit as admin
        should not recognise other users as admin
        """
        self.assertTrue(routes.is_admin("admin"))
        self.assertTrue(routes.is_admin("mit"))
        self.assertFalse(routes.is_admin("user"))
        self.assertFalse(routes.is_admin(""))

    def test_format_string_to_list(self):
        self.assertEqual(routes.format_string_to_list(
            "a, b, c"), ['a', 'b', 'c'])
        self.assertEqual(routes.format_string_to_list(
            "a, b, c", False), ['a, b, c'])


if __name__ == '__main__':
    unittest.main()
