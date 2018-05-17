import argparse
import asyncio
import logging
import sys
import xml.etree.ElementTree as ET

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError


from site_pinger.core.conf import Config
from site_pinger.core.email_sender import EmailSender

CONF_PATH = 'site_pinger_conf.ini'
EMAIL_HEADER = 'Site Pinger Result'
TIMEOUT = 60


async def check_site(check_url, session):
    try:
        async with session.head(check_url, allow_redirects=True) as resp:
            return check_url, resp.status
    except ClientConnectorError:
        return check_url, 'Error'


async def get_urls_from_sitemap(base_url, sitemap_url, session):
    try:
        async with session.get(base_url + sitemap_url) as resp:
            content = await resp.text()
            root = ET.fromstring(content)
            urls = [tag[0].text for tag in root]
            return base_url, urls
    except ClientConnectorError:
        return base_url, False


async def sitemap_urls_task(sitemap_confs, default_conf, session, options):
    sitemap_tasks = []
    for sitemap_conf in sitemap_confs:
        sitemap_url = sitemap_conf.get('sitemap', default_conf['sitemap'])
        base_url = sitemap_conf.get('url', None)
        if base_url is None:
            continue
        sitemap_tasks.append(get_urls_from_sitemap(base_url, sitemap_url, session))

    done, pending = await asyncio.wait(sitemap_tasks, timeout=options.timeout)
    check_urls_list = []
    for future in done:
        check_urls_list.append(future.result())
    result = {}
    for base_url, check_urls in check_urls_list:
        if check_urls is False:
            result[base_url] = [('sitemap is wrong', '')]
            continue
        result[base_url] = []
        for i in range(0, len(check_urls), default_conf['async_num']):
            tasks = []
            tasks.extend([check_site(check_url, session) for check_url in check_urls[i:i+default_conf['async_num']]])
            done, pending = await asyncio.wait(tasks, timeout=options.timeout)
            for future in done:
                result[base_url].append(future.result())
    return result


async def static_urls_task(static_urls, default_conf, session, options):
    result = {}
    for static_url in static_urls:
        tasks = []
        check_urls = static_url.get('urls', default_conf['urls']).split(',')
        check_urls.append('/')
        base_url = static_url['url']
        tasks.extend([check_site(base_url+check_url, session) for check_url in check_urls])
        done, pending = await asyncio.wait(tasks)
        result[static_url['url']] = []
        for future in done:
            result[static_url['url']].append(future.result())
    return result


async def run_checks(urls_conf, options):
    async with aiohttp.ClientSession() as session:
        tasks = [
            sitemap_urls_task(urls_conf.get_urls_with_sitemap(), urls_conf.default, session, options),
            static_urls_task(urls_conf.get_urls_without_sitemap(), urls_conf.default, session, options),
        ]
        done, pending = await asyncio.wait(tasks)
        result = {}
        for future in done:
            result.update(future.result())

        text, error_sum = generate_message(result)
        if error_sum:
            logging.info(text)
            if options.email:
                sender = EmailSender(urls_conf.email)
                sender.send(options.email_header, text)
        else:
            logging.info("All sites don't have problems.")


def generate_message(result):
    text = ''
    error_sum = 0
    for base_url, urls in result.items():
        text += '%s:\n' % base_url
        error_url_num = 0
        for url, status in urls:
            if status != 200:
                text += '\t{0:<100} - {1}\n'.format(url, status)
                error_url_num += 1
        if not error_url_num:
            text += "\tsite don't have problems"
        text += '\n\n'
        error_sum += error_url_num
    return text, error_sum


def base(options):
    Config.parse_config(options.config)
    if len(Config.errors):
        logging.warning(Config.get_errors())
    if Config.is_critical_error:
        logging.error('You have critical error in config file')
        return
    if Config.is_email_error:
        logging.warning('You have email config errors, send to email off')
        options.email = False

    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(run_checks(Config, options))
    ioloop.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--timeout", default=TIMEOUT, help="time out for async tasks", type=int)
    parser.add_argument("-l", "--log", default=None, help='log file path')
    parser.add_argument("-d", "--debug", default=False, help='debug logging', action="store_true")
    parser.add_argument("-e", "--email", default=True, help='receiver email', action="store_true")
    parser.add_argument("-c", "--config", default=CONF_PATH, help="config file path", nargs=1)
    parser.add_argument("--email-header", default=EMAIL_HEADER, help="header for email", nargs=1)

    opts = parser.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO if not opts.debug else logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

    try:
        logging.info('Start program')
        base(opts)
    except KeyboardInterrupt:
        logging.info('Program exit')
    except Exception as e:
        logging.exception("Unexpected error: %s" % e)
        sys.exit(1)
    finally:
        logging.info('End program')

