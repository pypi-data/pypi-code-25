from functools import wraps, partial

from werkzeug.exceptions import BadRequest, InternalServerError


__all__ = ["instance_args", "compose_decorator", "jsonify", "regular_handler"]


def instance_args(func):
    """装饰器对函数参数进行转换，如果参数为类型，转换为实例（调用默认构造函数），否则按原参数传入"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        args = [(v() if type(v) == type else v) for v in args]
        kwargs = {k: (v() if type(v) == type else v) for k, v in kwargs.items()}
        return func(*args, **kwargs)
    return decorated_function


def compose_decorator(*decorators):
    """装饰器用于合并多个装饰器"""
    def decorator(func):
        for decorator_ in decorators:
            func = decorator_(func)
        return func
    return decorator


def jsonify(func=None, **options):
    """装饰器对函数的返回结果使用 flask.jsonify 转换"""
    from flask import jsonify as jsonify_
    
    if func is None:
        return partial(jsonify, **options)

    @wraps(func)
    def decorated_function(*args, **kwargs):
        return jsonify_(func(*args, **kwargs), **kwargs)
    return decorated_function


@instance_args
def regular_handler(in_schema=None, out_schema=None):
    """装饰器将 Flask 请求数据按照 in_schema 验证并注入有效数据为函数的第一个参数"""
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if in_schema:
                request_data = _validate_request_data(in_schema, _get_request_data())
                result = func(request_data, *args, **kwargs)
            else:
                result = func(*args, **kwargs)
            if out_schema:
                result = _regular_result(out_schema, result)
            return result
        return decorated_function
    return decorator


def _get_request_data():
    from flask import request
    return request.args.to_dict(flat=False) if request.method == "GET" else request.get_json(force=True)


def _validate_request_data(schema, request_data):
    data, errors = schema.load(request_data)
    if errors:
        raise BadRequest(errors)
    return data


def _regular_result(schema, result):
    if schema:
        many = isinstance(result, (list, tuple))
        rv, errors = schema.dump(result, many=many)
        if errors:
            raise InternalServerError(errors)
        return rv
    return result
