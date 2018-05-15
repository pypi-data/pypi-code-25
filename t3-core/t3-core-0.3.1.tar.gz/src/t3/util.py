def get_response_type(code):
    if 100 <= code <= 199:
        return 'informational'
    if 200 <= code <= 299:
        return 'success'
    if 300 <= code <= 399:
        return 'redirect'
    if 400 <= code <= 499:
        return 'client_error'
    if 500 <= code <= 599:
        return 'server_error'
    return None
