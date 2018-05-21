from collections import deque


class SpiralMatrix(object):
    def __init__(self, matrix, clockwise=True):
        self.__matrix = matrix
        self.__clockwise = clockwise

    def __reversed__(self):
        return SpiralMatrix(self.__matrix, clockwise=not self.__clockwise)

    def __iter__(self):
        if not self.__matrix or not self.__matrix[0]:
            return

        # Create a duplicate of the original matrix using a deque. This allows
        # us to destructively modify the duplicate without affecting the input
        deques = deque([deque(vector) for vector in self.__matrix])

        while len(deques) and len(deques[0]):
            if self.__clockwise:
                for item in deques.popleft():
                    yield item

                for vector in deques:
                    yield vector.pop()

                if len(deques):
                    for item in reversed(deques.pop()):
                        yield item

                for vector in reversed(deques):
                    if len(vector):
                        yield vector.popleft()
            else:
                for vector in deques:
                    yield vector.popleft()

                for item in deques.pop():
                    yield item

                for vector in reversed(deques):
                    if len(vector):
                        yield vector.pop()

                if len(deques):
                    for item in reversed(deques.popleft()):
                        yield item
