class Parent():
    @property
    def foo(self):
        return self._foo

    @foo.setter
    def foo(self, value):
        self._foo = value

class Child(Parent):
    @property
    def foo(self):
        return self._foo + 'getchild'

    @foo.setter
    def foo(self, value):
        self._foo = value + 'setchild'

