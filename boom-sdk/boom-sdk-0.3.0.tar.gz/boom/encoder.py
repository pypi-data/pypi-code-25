import decimal
import json


class BoomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            # Note: this is OK for Python 2.7+ due to better precision in float conversion and rounding
            return float(obj)

        return json.JSONEncoder.default(self, obj)
