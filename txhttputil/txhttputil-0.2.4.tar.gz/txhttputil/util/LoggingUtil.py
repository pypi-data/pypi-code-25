"""
 * Created by Synerty Pty Ltd
 *
 * This software is open source, the MIT license applies.
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
"""

import logging

LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s:%(message)s'
DATE_FORMAT = '%d-%b-%Y %H:%M:%S'


def setupLogging():
    logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT, level=logging.DEBUG)

    logging.getLogger('suds.client').setLevel(logging.INFO)
    logging.getLogger('suds.transport').setLevel(logging.INFO)
    logging.getLogger('suds.resolver').setLevel(logging.INFO)
    logging.getLogger('suds.mx.core').setLevel(logging.INFO)
    logging.getLogger('suds.mx.literal').setLevel(logging.INFO)
    logging.getLogger('suds.metrics').setLevel(logging.INFO)
    logging.getLogger('suds.wsdl').setLevel(logging.INFO)
    logging.getLogger('suds.xsd.schema').setLevel(logging.INFO)
    logging.getLogger('suds.xsd.query').setLevel(logging.INFO)
    logging.getLogger('suds.xsd.sxbasic').setLevel(logging.INFO)
    logging.getLogger('suds.xsd.sxbase').setLevel(logging.INFO)
    logging.getLogger('suds.umx.typed').setLevel(logging.INFO)
