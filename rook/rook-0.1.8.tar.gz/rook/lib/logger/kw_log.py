import logging

from .logging_types import LogType


class KWLogger(logging.LoggerAdapter):

    def __init__(self, name, extra_tags=None):
        self.extra_tags = extra_tags or []
        self.warn = self.warning
        return super(KWLogger, self).__init__(name, {})

    def __getattr__(self, item):
        # in case we don't have a function, delagate it to the logger
        return getattr(self.logger, item)

    def process(self, msg, kwargs):
        return msg, self.__kwargs_to_rookout_extra(msg, kwargs)

    def __kwargs_to_rookout_extra(self, msg, kwargs):
        rookout_extra = {"extraTags": self.extra_tags} if self.extra_tags else {}
        for k, v in kwargs.items():
            if k == "extra":
                rookout_extra.update(v)
            else:
                field_type = LogType.get_type(k)
                if field_type:
                    try:
                        rookout_extra[k] = field_type(v)
                    except Exception as e:
                        rookout_extra["kw_errors"] = rookout_extra.get("kw_errors", []) + [
                            "Error convert field {}".format(v)]
                else:
                    rookout_extra["kw_errors"] = rookout_extra.get("kw_errors", []) + [
                        "Missing Kw field {}".format(v)]

        if not rookout_extra:
            return {}
        rookout_extra["message"] = msg
        return {"extra": {"rookout_extra": rookout_extra}}
