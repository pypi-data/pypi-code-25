from rest_framework.fields import Field
from rest_framework import serializers


class PointField(Field):

    def to_internal_value(self, data):
        """
        Transform the *incoming* primitive data into a native value.
        """
        raise NotImplementedError(
            '{cls}.to_internal_value() must be implemented.'.format(
                cls=self.__class__.__name__
            )
        )

    def to_representation(self, value):
        if value == 'empty':
            return {
                'lat': None,
                'lng': None
            }
        return {
            'lat': value.y,
            'lng': value.x
        }

    def get_attribute(self, instance):
        attr = super().get_attribute(instance)
        if not attr:
            return 'empty'
        return attr


class DictSerializer(serializers.ListSerializer):

    def __init__(self, *args, **kwargs):
        self.key = kwargs.pop('key')
        super().__init__(*args, **kwargs)

    def to_representation(self, data):

        r = super().to_representation(data)
        r = [
            {**i, **{self.key: str(i[self.key])}} for i in r
        ]
        # str представление для ключа, чтобы '1': {'id': '1'} было строковым с обоих сторон
        return {
            str(i[self.key]): i for i in r
        }

    @property
    def data(self):
        return super(serializers.ListSerializer, self).data


class KeyValueSerializer(serializers.ModelSerializer):
    """
    Меняет лист представление объектов на словарь с выбранным ключом объекта
    {
        1: {
            id: 1
        },
        2: {
            id: 2
        }
    }  
    """
    key = 'id'

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        return DictSerializer(*args, **kwargs, key=cls.key)
