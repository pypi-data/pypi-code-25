try:
    from .unix import input_edit_text
except ImportError:
    from .windows import input_edit_text
