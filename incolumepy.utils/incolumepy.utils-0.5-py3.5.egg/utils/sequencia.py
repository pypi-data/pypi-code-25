import unittest
from math import sqrt


class Sequencia:

    class Fibonacci:
        def __init__(self):
            self.seq = [1, 1]

        def __next__(self):
            self.seq.append(sum(self.seq))
            return self.seq.pop(0)

        def __iter__(self):
            return Sequencia.Fibonacci()

    class Naturais:
        def __init__(self):
            self.lista = [0]

        def __next__(self):
            self.lista.append(self.lista[0] + 1)
            return self.lista.pop(0)

        def __iter__(self):
            return Sequencia.Naturais()


    class Pares:
        def __init__(self):
            self.lista = [2]

        def __next__(self):
            self.lista.append(self.lista[0] + 2)
            return self.lista.pop(0)

        def __iter__(self):
            return Sequencia.Pares()

        def ispar(self, num):
            return num % 2 == 0

    class Impares:
        def __init__(self):
            self.lista = [1]

        def __next__(self):
            self.lista.append(self.lista[0] + 2)
            return self.lista.pop(0)

        def __iter__(self):
            return Sequencia.Impares()

        def isimpar(self, num):
            return num % 2 == 1

    class Primos:
        '''
        Números primos são os números naturais maiores que 1 e têm apenas dois divisores diferentes: o 1 e ele mesmo.
        '''
        primos = []

        def __init__(self):
            self.primos = [2, 3, 5, 7]
            self.seq = Sequencia.Naturais()

        def __next__(self):
            while 1:
                value = self.seq.__next__()
                if self.isprimo(value):
                    self.primos.append(value)
                    return self.primos[-1]

        def __iter__(self):
            return Sequencia.Primos()

        def isprimo(self, numero):

            if numero in self.primos:
                return True

            if numero <= 1:
                return False

            if Sequencia.Pares().ispar(numero):
                return False

            for i in range(3, numero + 1, 2):

                if (i != numero):
                    if (numero % i == 0):
                        return False
                    if  (i > sqrt(numero)):
                        continue
                else:
                    self.primos.append(numero)
                    return True

class UtilsTest(unittest.TestCase):
    def test_primos(self):
        a = Sequencia.Primos()
        l = []

        for i in range(10):
            l.append(a.__next__())
        self.assert_(l == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
        self.assertEquals(a.__next__(), 31)
        self.assertEquals(a.__next__(), 37)
        self.assertEquals(a.__next__(), 41)
        self.assertEquals(a.__next__(), 43)
        a = Sequencia.Primos()
        l.clear()
        for i in range(1000):
            l.append(a.__next__())
        self.assertEquals(a.__next__(), 7927)
        self.assertIn(7669, l)

        a = Sequencia.Primos()
        l.clear()
        for i in range(2000):
            l.append(a.__next__())
        self.assertEquals(a.__next__(), 17393)
        self.assertIn(17389, l)
        self.assertFalse(a.isprimo(
            4224696333392304878706725602341482782579852840250681098010280137314308584370130707224123599639141511088446087538909603607640194711643596029271983312598737326253555802606991585915229492453904998722256795316982874482472992263901833716778060607011615497886719879858311468870876264597369086722884023654422295243347964480139515349562972087652656069529806499841977448720155612802665404554171717881930324025204312082516817125))

        with self.assertRaises(OverflowError):
            a.isprimo(
                422469633339230487870672560234148278257985284025068109801028013731430858437013070722412359963914151108844608753890960360764019471164359602927198331259873732625355580260699158591522949245390499872225679531698287448247299226390183371677806060701161549788671987985831146887087626459736908672288402365442229524334796448013951534956297208765265606952980649984197744872015561280266540455417171788193032402520431208251681712513)

    def test_fibonatti(self):
        a = Sequencia.Fibonacci()
        l = []
        for i in range(10):
            l.append(a.__next__())
        self.assert_(l == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55])
        self.assert_(a.__next__() == 89)
        self.assert_(a.__next__() == 144)
        self.assertEquals(a.__next__(), 233)
        self.assertEquals(a.__next__(), 377)
        self.assertEquals(a.__next__(), 610)
        self.assertEquals(a.__next__(), 987)
        a = Sequencia.Fibonacci()
        l.clear()
        for i in range(2000):
            l.append(a.__next__())
        self.assertIn(
            4224696333392304878706725602341482782579852840250681098010280137314308584370130707224123599639141511088446087538909603607640194711643596029271983312598737326253555802606991585915229492453904998722256795316982874482472992263901833716778060607011615497886719879858311468870876264597369086722884023654422295243347964480139515349562972087652656069529806499841977448720155612802665404554171717881930324025204312082516817125,
            l)

    def test_impares(self):
        a = Sequencia.Impares()
        l = []
        for i in range(10):
            l.append(a.__next__())
        self.assert_(l == [1, 3, 5, 7, 9, 11, 13, 15, 17, 19])
        self.assert_(a.__next__() == 21)
        self.assert_(a.__next__() == 23)
        self.assert_(a.__next__() == 25)

    def test_pares(self):
        b = Sequencia.Pares()
        l = list()
        for i in range(10):
            l.append(b.__next__())
        self.assert_(l == [2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
        self.assert_(b.__next__() == 22)
        self.assert_(b.__next__() == 24)
        self.assert_(b.__next__() == 26)

    def test_naturais(self):
        print('Naturais ')
        a = Sequencia.Naturais()
        self.assert_(a.__next__() == 0)
        self.assert_(a.__next__() == 1)
        self.assert_(a.__next__() == 2)
        self.assert_(a.__next__() == 3)
        self.assert_(a.__next__() == 4)
        self.assert_(a.__next__() == 5)
        self.assert_(a.__next__() == 6)
        self.assert_(a.__next__() == 7)
        self.assert_(a.__next__() == 8)
        self.assert_(a.__next__() == 9)
        self.assert_(a.__next__() == 10)
        for i in range(10):
            a.__next__()
        self.assert_(a.__next__() == 21)
        l = list()
        for i in range(5):
            l.append(a.__next__())
        self.assert_(l == [22, 23, 24, 25,26])


def Main():
    print('\nPrimos')
    a = Sequencia.Primos()
    for i in range(1, 1051):
        print(i, a.__next__())




if __name__ == '__main__':
    Main()
