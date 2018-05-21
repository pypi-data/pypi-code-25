import json
import logging
from restclients_core.exceptions import DataFailureException
from uw_iasystem.dao import IASystem_DAO
from uw_iasystem.exceptions import TermEvalNotCreated
from uw_iasystem.util.thread import ThreadWithResponse


logger = logging.getLogger(__name__)


def get_resource(url, domain):
    threads = []
    for dao in IASystem_DAO(domain):
        t = ThreadWithResponse(target=__get_resource, args=(dao, url))
        t.start()
        threads.append((t, dao.service_name()))

    for t, k in threads:
        t.join()
        if t.response is not None:
            data = t.response
            if data.get('collection') and\
               data.get('collection').get('items'):
                return t.response

        if t.exception is not None:
            logger.error("%s: %s" % (k, t.exception))
            raise t.exception
    return None


def __get_resource(dao, url):
    """
    Issue a GET request to IASystem with the given url
    and return a response in Collection+json format.
    :returns: http response with content in json
    """
    headers = {"Accept": "application/vnd.collection+json"}
    response = dao.getURL(url, headers)
    status = response.status
    logger.debug("%s ==status==> %s", url, status)

    if status != 200:
        message = response.data

        if status == 404:
            # the URL not exists on the specific domain
            return None

        if status == 400:
            if "Term is out of range" in message:
                raise TermEvalNotCreated(url, status, message)

        raise DataFailureException(url, status, message)

    return json.loads(response.data)
