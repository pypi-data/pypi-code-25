"""
Handling the actual upload
"""
import json
import requests

__all__ = ('upload',)


def stream_raw_sse(mkrequest, *pargs, _last_event_id=None, headers=None, **kwargs):
    """
    Streams Server-Sent Events, each event produced as a sequence of
    (field, value) pairs.

    Does not handle reconnection, etc.
    """
    if headers is None:
        headers = {}
    headers['Accept'] = 'text/event-stream'
    headers['Cache-Control'] = 'no-cache'
    # Per https://html.spec.whatwg.org/multipage/server-sent-events.html#sse-processing-model
    if _last_event_id is not None:
        headers['Last-Event-ID'] = _last_event_id

    with mkrequest(*pargs, headers=headers, stream=True, **kwargs) as resp:
        resp.raise_for_status()
        fields = []
        for line in resp.iter_lines(decode_unicode=True):
            # https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation
            if not line:
                yield fields
                fields = []
            elif line.startswith(':'):
                pass
            elif ':' in line:
                field, value = line.split(':', 1)
                if value.startswith(' '):
                    value = value[1:]
                fields += [(field, value)]
            else:  # Non-blank, without a colon
                fields += [(line, '')]


def less_raw(msgs):
    """
    Wrap around stream_raw_sse() to get spiro-deploy data.
    """
    for msg in msgs:
        msg = dict(msg)
        yield msg.get('event'), json.loads(msg.get('data'))


def upload(url, token, tarball, project, deployment, highstate=True, sslverify=True):
    """
    Do the upload&deploy thing
    """
    fields = {
        'project': project,
        'deployment': deployment,
    }
    if highstate:
        fields['highstate'] = True
    tarball.seek(0)
    files = {
        'bundle': tarball,
    }
    for event, data in less_raw(stream_raw_sse(
        requests.post, 
        url,
        data=fields, 
        files=files,
        headers={'Authorization': 'bearer {}'.format(token)},
        verify=sslverify,
    )):
        yield event, data

