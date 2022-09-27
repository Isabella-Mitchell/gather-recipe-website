import unittest
import gather
from gather import routes

class TestRoutes(unittest.TestCase):
    def test_is_admin(self):
        self.assertTrue(routes.is_admin("admin"))

if __name__ == '__main__':
    unittest.main()