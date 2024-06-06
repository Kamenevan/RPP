from triangle_class import Triangle, IncorrectTriangleSides
import pytest #библиотека для проведения тестирования
def test_triangle_creation():
    with pytest.raises(IncorrectTriangleSides):
        Triangle(0, 0, 0)

    with pytest.raises(IncorrectTriangleSides):
        Triangle(-1, 2, 3)

    with pytest.raises(IncorrectTriangleSides):
        Triangle(1, 1, 3)
def test_triangle_methods():
    triangle1 = Triangle(3, 4, 5)
    assert triangle1.triangle_type() == "разносторонний"
    assert triangle1.perimeter() == 12

    triangle2 = Triangle(5, 5, 5)
    assert triangle2.triangle_type() == "равносторонний"
    assert triangle2.perimeter() == 15

    triangle3 = Triangle(7, 7, 10)
    assert triangle3.triangle_type() == "равнобедренный"
    assert triangle3.perimeter() == 24
if __name__ == "__main__":
    pytest.main()
