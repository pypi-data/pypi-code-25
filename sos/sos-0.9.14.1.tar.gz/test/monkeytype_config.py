from types import CodeType
from monkeytype.tracing import CodeFilter
from monkeytype.config import DefaultConfig, default_code_filter

class MyConfig(DefaultConfig):

    def code_filter(self) -> CodeFilter:
        """Default code filter excludes standard library & site-packages."""
        def sos_code_filter(code: CodeType) -> bool:
            """A CodeFilter to exclude stdlib and site-packages."""
            return 'sos' in code.co_filename or default_code_filter(code)
        return sos_code_filter

CONFIG = MyConfig()
