# coding: utf-8

DEFAULT_HTTP_BIND = ""
DEFAULT_HTTP_HOST = "localhost"
DEFAULT_HTTP_PORT = 11080

RULE_API_REST_BASE_PATH = r"/api/rest/rules"

RULE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": ["integer", "string"]},
        "description": {"type": "string"},
        "request": {"$ref": "#/definitions/request"},
        "response": {"$ref": "#/definitions/response"},
    },
    "required": ["request", "response"],
    "additionalProperties": False,

    "definitions": {
        "request": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "method": {"type": "string"},
                "queries": {"type": "object"},
                "headers": {"type": "object"},
                "body": {"type": ["string", "array", "object"]},
            },
            "required": ["path", "method"],
            "additionalProperties": False
        },
        "response": {
            "type": "object",
            "properties": {
                "delay": {"type": "number"},
                "body": {"type": ["string", "array", "object"]},
                "status": {"type": "integer"},
                "headers": {"type": "object"},
            },
            "additionalProperties": False
        },
    }
}
