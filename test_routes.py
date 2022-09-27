import unittest
import gather
from gather import routes

class TestRoutes(unittest.TestCase):
# use python test_routes.py to run tests
    def test_is_admin(self):
        self.assertTrue(routes.is_admin("admin"))
        self.assertFalse(routes.is_admin("user"))        

if __name__ == '__main__':
    unittest.main()