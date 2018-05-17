

class PositiveInteger(int):
    def __new__(cls, value):
        print(cls)
        print(super(PositiveInteger, cls))
        return int.__new__(cls, abs(value))

i = PositiveInteger(-3)
