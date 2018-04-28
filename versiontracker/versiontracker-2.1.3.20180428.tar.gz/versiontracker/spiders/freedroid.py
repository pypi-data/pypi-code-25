from ftplib import FTP

from ..items import Item

from . import Spider


class Freedroid(Spider):
    name = 'freedroid'

    def parse(self, response):
        xpath = '//span[@id=\'download_lastversion\']/text()'
        package_string = response.xpath(xpath).extract_first().strip()
        package_folder = ".".join(package_string.split(".")[:2])
        package_sources_subdir = \
            "pub/freedroid/{package_folder}/{package}.tar.gz".format(
                package=package_string, package_folder=package_folder)
        version = "-".join(package_string.split("-")[1:])
        ftp_domain = "ftp.osuosl.org"
        ftp = FTP(ftp_domain)
        ftp.login()
        data = ftp.sendcmd("MDTM {}".format(package_sources_subdir))
        return Item(date=data.split(" ")[1],
                    response=response,
                    url="ftp://{}/{}".format(
                        ftp_domain, package_sources_subdir),
                    version=version)

    def first_request(self, data):
        return 'http://www.freedroid.org/'
