"""\
Mock HTTP server. Asks you for a JSON response everytime you \
visit a path for the first time.
"""

import json
import sys

from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response


BANNER = """\
┏┳┓┏━┓┏━╸╻┏ ┏━┓┏━╸┏━┓
┃┃┃┃ ┃┃  ┣┻┓┗━┓┣╸ ┣┳┛
╹ ╹┗━┛┗━╸╹ ╹┗━┛┗━╸╹┗╸"""

known_routes = {}


@Request.application
def application(request):
    response_text = known_routes.get(request.path)
    if not response_text:
        response_text = _ask_for_response(request.path)
        if response_text:
            known_routes[request.path] = response_text
    return Response(response_text,
                    headers={
                        "content-type": "application/json"
                    })


class NotJsonObjectException(BaseException):
    pass


def _ask_for_response(path):
    print(">>> Insert JSON response for {}. Ctrl-D to submit.".format(path))
    while True:
        input_ = "\n".join(sys.stdin.readlines()) or ""
        try:
            read_json = json.loads(input_)
            if type(read_json) is not dict:
                raise NotJsonObjectException
            if read_json:
                print(">>> JSON accepted")
            break
        except json.decoder.JSONDecodeError:
            if input_:
                print("!!! It's not a valid JSON. Try again.")
            else:
                print(">>> No response for {} specified this time.".format(path))
                break
        except NotJsonObjectException:
            print("!!! It's not JSON object. Try again.")
    return input_


def main():
    import argparse

    parser = argparse.ArgumentParser(description="{}\n\n{}".format(BANNER, __doc__),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", "--port", type=int, default=8080,
                        help="Port to run the server on. Defaults to 8080.")
    args = parser.parse_args()
    _run(args.port)


def _run(port):
    print(BANNER)
    run_simple("0.0.0.0", port, application)


if __name__ == "__main__":
    main()
