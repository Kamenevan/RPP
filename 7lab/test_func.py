import unittest#модуль для создания модульных тестов
from triangle_func import get_triangle_type, IncorrectTriangleSides
class TestTriangleFunction(unittest.TestCase):
    def test_equilateral(self):
        self.assertEqual(get_triangle_type(5, 5, 5), "равносторонний")
    def test_isosceles(self):
        self.assertEqual(get_triangle_type(5, 5, 3), "равнобедренный")
    def test_nonequilateral(self):
        self.assertEqual(get_triangle_type(3, 4, 5), "разносторонний")
    #для некорректной длины стороны
    def test_invalid_side_length(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-1, 2, 3)
    def test_invalid_triangle(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 1, 3)
if __name__ == '__main__':
    unittest.main()
