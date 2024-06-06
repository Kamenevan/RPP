class IncorrectTriangleSides(Exception):
    pass
def get_triangle_type(a, b, c):#функция для определения типа треугольника (на основе длин его сторон)
    #проверка на положительность
    if a <= 0 or b <= 0 or c <= 0:
        raise IncorrectTriangleSides("Длины сторон должны быть положительными")
    #проверка неравенста: третья сторона должна быть меньше суммы двух других сторон
    if a + b <= c or a + c <= b or b + c <= a:
        raise IncorrectTriangleSides("Недопустимые длины сторон для треугольника")
    #Проверка равносторонний треугольник
    if a == b == c:
        return "равносторонний"
    #Проверка равнобедренный треугольник
    elif a == b or a == c or b == c:
        return "равнобедренный"
    else:
        return "разносторонний"
