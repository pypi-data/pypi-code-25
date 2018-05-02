import json


def build(response, is_success=True, description=''):
    data = None
    if response:
        data = response.to_resource()

    resource = json.dumps({
        "success": is_success,
        "description": description,
        "data": data
    }, indent=4, sort_keys=True, default=str)
    return json.loads(resource)
