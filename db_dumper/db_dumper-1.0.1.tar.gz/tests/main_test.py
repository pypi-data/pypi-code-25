from pytest import raises
from db_dumper import load, dump


class Save(Exception):
    pass


def save(obj):
    raise Save()


def dump_object(obj):
    return {x: getattr(obj, x) for x in dir(obj) if not x.startswith('_')}


class DummyObject:

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __eq__(self, instance):
        return instance.name == self.name and instance.age == self.age


def test_dump():
    o = DummyObject('Chris Norman', 28)
    data = dump([o], dump_object)
    assert len(data) is 1
    assert list(data.keys()) == [DummyObject.__name__]
    assert list(
        data.values()
    )[0][0] == {
        'name': o.name,
        'age': o.age
    }


def test_load():
    me = DummyObject('Chris Norman', 28)
    dog = DummyObject('Fliss', 10)
    d = dump([me, dog], dump_object)
    objects = load(d, [DummyObject])
    assert len(objects) is 2
    loaded_me, loaded_dog = objects
    assert loaded_me == me
    assert loaded_dog == dog


def test_object_save():
    o = DummyObject('Chris', 28)
    objects = [o]
    data = dump(objects, dump_object)
    with raises(Save):
        load(data, [DummyObject], object_save=save)


def test_no_objects():
    objects = load({}, [DummyObject])
    assert not objects
