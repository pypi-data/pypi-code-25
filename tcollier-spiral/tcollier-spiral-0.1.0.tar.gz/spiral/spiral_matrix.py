from collections import deque


class SpiralMatrix(object):
    def __init__(self, matrix):
        self.__matrix = matrix

    def __iter__(self):
        if not self.__matrix or not self.__matrix[0]:
            return

        # Create a duplicate of the original matrix using a deque. This allows
        # us to destructively modify the duplicate without affecting the input
        deques = deque([deque(vector) for vector in self.__matrix])

        while len(deques) and len(deques[0]):
            for item in deques.popleft():
                yield item

            for vector in deques:
                if len(vector):
                    yield vector.pop()

            if len(deques):
                for item in reversed(deques.pop()):
                    yield item

            for vector in reversed(deques):
                if len(vector):
                    yield vector.popleft()
