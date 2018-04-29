# -*- coding: utf-8 -*-
import json

from datetime import datetime as type_datetime


# 根据表单请求包装实体
def wrap_entity_by_form_data(entity, request):
    public_fields = get_public_fields_of_entity(entity)
    for key, value in request.form.items():
        if key in public_fields:
            if hasattr(entity, key):
                setattr(entity, key, value)
    return entity


# 获取实体类的公开属性
def get_public_fields_of_entity(entity):
    public_fields = []
    if hasattr(entity, '_sa_instance_state'):
        keys = entity._sa_instance_state.attrs._data.keys()
        for field in keys:
            public_fields.append(field)
    return public_fields


# 实体类转换成字典
def entity_to_dict(instance):
    fields = get_public_fields_of_entity(instance)
    result_dict = {}
    for field in fields:
        result_dict[field] = get_entity_value_or_empty(instance, field)
    return result_dict


# 获取对象的字段值，如果没有该字段则返回空字符串
def get_entity_value_or_empty(entity, field):
    if entity is not None and field is not None and hasattr(entity, field):
        value = getattr(entity, field)
        if value is not None:
            return value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, type_datetime) else value
    return ''


# 实体类数据转换为JSON
def dump_entity_data_to_json(data):
    return json.dumps(data, default=entity_to_dict, ensure_ascii=False)
