import unittest

from app.calc import add, substract
# app.app.calc but from docker perspecti app is the root so app.calc


class Test_test_1_calc(unittest.TestCase):

    def test_add_numbers(self):
        """Test that two numbers are added together TDD"""
        self.assertEqual(add(5, 5), 10)

    def test_substract_numbers(self):
        """Test that values are substracted and returned TDD"""
        self.assertEqual(substract(5, 4), 1)


if __name__ == '__main__':
    unittest.main()
