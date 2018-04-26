import logging

import requests

from muted_http_request_randomizer.requests.parsers.UrlParser import UrlParser
from muted_http_request_randomizer.requests.proxy.ProxyObject import ProxyObject, AnonymityLevel

logger = logging.getLogger()
__author__ = 'pgaref'


class ProxyForEuParser(UrlParser):
    def __init__(self, id, web_url, bandwidth=None, timeout=None):
        UrlParser.__init__(self, id=id, web_url=web_url, bandwidth_KBs=bandwidth, timeout=timeout)

    def parse_proxyList(self):
        curr_proxy_list = []
        try:
            response = requests.get(self.get_url(), timeout=self.timeout)

            if not response.ok:
                logger.warning("Proxy Provider url failed: {}".format(self.get_url()))
                return []

            content = response.text.split('\n')
            for i, line in enumerate(content):
                if i > 3:
                    if not line:
                        break
                    proxy_obj = self.create_proxy_object(line.split())
                    # Avoid Straggler proxies and make sure it is a Valid Proxy Address
                    if proxy_obj is not None and UrlParser.valid_ip_port(proxy_obj.get_address()):
                        curr_proxy_list.append(proxy_obj)
                    else:
                        # print("Proxy Invalid: {}".format(line))
                        logger.debug("Proxy Invalid: {}".format(line))
        except AttributeError as e:
            logger.error("Provider {0} failed with Attribute error: {1}".format(self.id, e))
            # print("Provider {0} failed with Attribute error: {1}".format(self.id, e))
        except KeyError as e:
            logger.error("Provider {0} failed with Key error: {1}".format(self.id, e))
            # print("Provider {0} failed with Key error: {1}".format(self.id, e))
        except Exception as e:
            logger.error("Provider {0} failed with Unknown error: {1}".format(self.id, e))
            # print("Provider {0} failed with Unknown error: {1}".format(self.id, e))
        finally:
            return curr_proxy_list

    def create_proxy_object(self, line):
        ip, port = line[0].split(':')
        anonymity, country = line[1].split('-')[:2]
        anonymity = AnonymityLevel.get(anonymity.strip())
        return ProxyObject(source=self.id, ip=ip, port=port,
                           anonymity_level=anonymity, country=country)

    def __str__(self):
        return "ProxyForEU Parser of '{0}' with required bandwidth: '{1}' KBs" \
            .format(self.url, self.minimum_bandwidth_in_KBs)
