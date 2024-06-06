class IncorrectTriangleSides(Exception):#класс для описания треугольника
    pass
class Triangle:
    def __init__(self, a, b, c):  #Определение конструктора класса
        if a <= 0 or b <= 0 or c <= 0:
            raise IncorrectTriangleSides("Длины сторон должны быть положительными")
        if a + b <= c or a + c <= b or b + c <= a:    #сумма двух сторон должна быть больше третьей стороны
            raise IncorrectTriangleSides("Недопустимые длины сторон для треугольника")
        self.a = a
        self.b = b
        self.c = c
    def triangle_type(self):
        if self.a == self.b == self.c:
            return "равносторонний"
        elif self.a == self.b or self.a == self.c or self.b == self.c:
            return "равнобедренный"
        else:
            return "разносторонний"
    #периметр треугольника
    def perimeter(self):
        return self.a + self.b + self.c #Возвращается сумма длин всех сторон треугольника

