#!/usr/bin/env python3

import csv
import datetime
import itertools
import os
import re
import sys

import attr
import backoff
import requests
import singer
import singer.stats
from singer import transform
from singer import utils


LOGGER = singer.get_logger()
SESSION = requests.Session()


CONFIG = {
    "app_id": None,
    "api_token": None,
}


STATE = {}


ENDPOINTS = {
    "installs": "/export/{app_id}/installs_report/v5",
    "in_app_events": "/export/{app_id}/in_app_events_report/v5"
}


def af_datetime_str_to_datetime(s):
    return datetime.datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S")


def get_start(key):
    if key in STATE:
        return  utils.strptime(STATE[key])

    if "start_date" in CONFIG:
        return  utils.strptime(CONFIG["start_date"])

    return datetime.datetime.now() - datetime.timedelta(days=30)


def get_stop(start_datetime):
    return min(start_datetime + datetime.timedelta(days=30), datetime.datetime.now())


def get_base_url():
    if "base_url" in CONFIG:
        return CONFIG["base_url"]
    else:
        return "https://hq.appsflyer.com"


def get_url(endpoint, **kwargs):
    if endpoint not in ENDPOINTS:
        raise ValueError("Invalid endpoint {}".format(endpoint))
    else:
        return get_base_url() + ENDPOINTS[endpoint].format(**kwargs)


def xform_datetime_field(record, field_name):
    record[field_name] = af_datetime_str_to_datetime(record[field_name]).isoformat()


def xform_boolean_field(record, field_name):
    if record[field_name].lower() == "TRUE".lower():
        record[field_name] = True
    else:
        record[field_name] = False


def xform_empty_strings_to_none(record):
    for key, value in record.items():
        if value == "":
            record[key] = None


def xform(record, schema):
    xform_empty_strings_to_none(record)
    xform_boolean_field(record, "wifi")
    xform_boolean_field(record, "is_retargeting")
    return transform.transform(record, schema)


@attr.s
class Stream(object):
    name = attr.ib()
    sync = attr.ib()


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schema(entity_name):
    schema = utils.load_json(get_abs_path('schemas/{}.json'.format(entity_name)))
    return schema


def giveup(exc):
    return exc.response is not None and 400 <= exc.response.status_code < 500


def parse_source_from_url(url):
    url_regex = re.compile(get_base_url() + r'.*/(\w+)_report/v5')
    match = url_regex.match(url)
    if match:
        return match.group(1)
    return None


@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException),
                      max_tries=5,
                      giveup=giveup,
                      factor=2)
@utils.ratelimit(10, 1)
def request(url, params=None):

    params = params or {}
    headers = {}

    if "user_agent" in CONFIG:
        headers["User-Agent"] = CONFIG["user_agent"]

    req = requests.Request("GET", url, params=params, headers=headers).prepare()
    LOGGER.info("GET %s", req.url)

    with singer.stats.Timer(source=parse_source_from_url(url)) as stats:
        resp = SESSION.send(req)
        stats.http_status_code = resp.status_code

    if resp.status_code >= 400:
        LOGGER.error("GET %s [%s - %s]", req.url, resp.status_code, resp.content)
        sys.exit(1)

    return resp


class RequestToCsvAdapter:
    def __init__(self, request_data):
        self.request_data_iter = request_data.iter_lines();

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.request_data_iter).decode("utf-8")


def sync_installs():

    schema = load_schema("raw_data/installations")
    singer.write_schema("installs", schema, [
        "event_time",
        "event_name",
        "appsflyer_id"
    ])

    # This order matters
    fieldnames = (
        "attributed_touch_type",
        "attributed_touch_time",
        "install_time",
        "event_time",
        "event_name",
        "event_value",
        "event_revenue",
        "event_revenue_currency",
        "event_revenue_usd",
        "event_source",
        "is_receipt_validated",
        "af_prt",
        "media_source",
        "af_channel",
        "af_keywords",
        "campaign",
        "af_c_id",
        "af_adset",
        "af_adset_id",
        "af_ad",
        "af_ad_id",
        "af_ad_type",
        "af_siteid",
        "af_sub_siteid",
        "af_sub1",
        "af_sub2",
        "af_sub3",
        "af_sub4",
        "af_sub5",
        "af_cost_model",
        "af_cost_value",
        "af_cost_currency",
        "contributor1_af_prt",
        "contributor1_media_source",
        "contributor1_campaign",
        "contributor1_touch_type",
        "contributor1_touch_time",
        "contributor2_af_prt",
        "contributor2_media_source",
        "contributor2_campaign",
        "contributor2_touch_type",
        "contributor2_touch_time",
        "contributor3_af_prt",
        "contributor3_media_source",
        "contributor3_campaign",
        "contributor3_touch_type",
        "contributor3_touch_time",
        "region",
        "country_code",
        "state",
        "city",
        "postal_code",
        "dma",
        "ip",
        "wifi",
        "operator",
        "carrier",
        "language",
        "appsflyer_id",
        "advertising_id",
        "idfa",
        "android_id",
        "customer_user_id",
        "imei",
        "idfv",
        "platform",
        "device_type",
        "os_version",
        "app_version",
        "sdk_version",
        "app_id",
        "app_name",
        "bundle_id",
        "is_retargeting",
        "retargeting_conversion_type",
        "af_attribution_lookback",
        "af_reengagement_window",
        "is_primary_attribution",
        "user_agent",
        "http_referrer",
        "original_url",
    )

    from_datetime = get_start("installs")
    to_datetime = get_stop(from_datetime)

    if to_datetime < from_datetime:
        LOGGER.error("to_datetime (%s) is less than from_endtime (%s).", to_datetime, from_datetime)
        return

    params = dict()
    params["from"] = from_datetime.strftime("%Y-%m-%d %H:%M")
    params["to"] = to_datetime.strftime("%Y-%m-%d %H:%M")
    params["api_token"] = CONFIG["api_token"]

    url = get_url("installs", app_id=CONFIG["app_id"])
    request_data = request(url, params)

    csv_data = RequestToCsvAdapter(request_data)
    reader = csv.DictReader(csv_data, fieldnames)

    next(reader) # Skip the heading row

    # AppsFlyer returns records in order of most recent first. So, we
    # need to reverse them in order to provide sensible STATE
    # checkpoints.  According to the API documentation, there may be
    # as many as 200,000 rows here but I don't have a better solution.
    rows = []
    for row in reader:
        rows.append(row)
    rows = reversed(rows)

    # Emit updated records with state checkpoint
    for i, row in enumerate(rows):
        record = xform(row, schema)
        singer.write_record("installs", record)
        utils.update_state(STATE, "installs", record["attributed_touch_time"])

        if (i % 250) == 0:
            singer.write_state(STATE)

    # Write out final state
    singer.write_state(STATE)


def sync_in_app_events():

    schema = load_schema("raw_data/in_app_events")
    singer.write_schema("in_app_events", schema, [
        "event_time",
        "event_name",
        "appsflyer_id"
    ])

    # This order matters
    fieldnames = (
        "attributed_touch_type",
        "attributed_touch_time",
        "install_time",
        "event_time",
        "event_name",
        "event_value",
        "event_revenue",
        "event_revenue_currency",
        "event_revenue_usd",
        "event_source",
        "is_receipt_validated",
        "af_prt",
        "media_source",
        "af_channel",
        "af_keywords",
        "campaign",
        "af_c_id",
        "af_adset",
        "af_adset_id",
        "af_ad",
        "af_ad_id",
        "af_ad_type",
        "af_siteid",
        "af_sub_siteid",
        "af_sub1",
        "af_sub2",
        "af_sub3",
        "af_sub4",
        "af_sub5",
        "af_cost_model",
        "af_cost_value",
        "af_cost_currency",
        "contributor1_af_prt",
        "contributor1_media_source",
        "contributor1_campaign",
        "contributor1_touch_type",
        "contributor1_touch_time",
        "contributor2_af_prt",
        "contributor2_media_source",
        "contributor2_campaign",
        "contributor2_touch_type",
        "contributor2_touch_time",
        "contributor3_af_prt",
        "contributor3_media_source",
        "contributor3_campaign",
        "contributor3_touch_type",
        "contributor3_touch_time",
        "region",
        "country_code",
        "state",
        "city",
        "postal_code",
        "dma",
        "ip",
        "wifi",
        "operator",
        "carrier",
        "language",
        "appsflyer_id",
        "advertising_id",
        "idfa",
        "android_id",
        "customer_user_id",
        "imei",
        "idfv",
        "platform",
        "device_type",
        "os_version",
        "app_version",
        "sdk_version",
        "app_id",
        "app_name",
        "bundle_id",
        "is_retargeting",
        "retargeting_conversion_type",
        "af_attribution_lookback",
        "af_reengagement_window",
        "is_primary_attribution",
        "user_agent",
        "http_referrer",
        "original_url",
    )

    from_datetime = get_start("in_app_events")
    to_datetime = get_stop(from_datetime)

    if to_datetime < from_datetime:
        LOGGER.error("to_datetime (%s) is less than from_endtime (%s).", to_datetime, from_datetime)
        return

    params = dict()
    params["from"] = from_datetime.strftime("%Y-%m-%d %H:%M")
    params["to"] = to_datetime.strftime("%Y-%m-%d %H:%M")
    params["api_token"] = CONFIG["api_token"]

    url = get_url("in_app_events", app_id=CONFIG["app_id"])
    request_data = request(url, params)

    csv_data = RequestToCsvAdapter(request_data)
    reader = csv.DictReader(csv_data, fieldnames)

    next(reader) # Skip the heading row

    # AppsFlyer returns records in order of most recent first. So, we
    # need to reverse them in order to provide sensible STATE
    # checkpoints.  According to the API documentation, there may be
    # as many as 200,000 rows here but I don't have a better solution.
    rows = []
    for row in reader:
        rows.append(row)
    rows = reversed(rows)

    # Emit updated records with state checkpoint
    for i, row in enumerate(rows):
        record = xform(row, schema)
        singer.write_record("in_app_events", record)
        utils.update_state(STATE, "in_app_events", record["event_time"])  # NOTE: This is different in each report

        if (i % 250) == 0:
            singer.write_state(STATE)

    # Write out final state
    singer.write_state(STATE)


STREAMS = [
    Stream("installs", sync_installs),
    Stream("in_app_events", sync_in_app_events)
]


def get_streams_to_sync(streams, state):
    target_stream = state.get("this_stream")
    result = streams
    if target_stream:
        result = list(itertools.dropwhile(lambda x: x.name != target_stream, streams))
    if not result:
        raise Exception('Unknown stream {} in state'.format(target_stream))
    return result


def do_sync():
    LOGGER.info("do_sync()")
    streams = get_streams_to_sync(STREAMS, STATE)
    LOGGER.info('Starting sync. Will sync these streams: %s', [stream.name for stream in streams])
    for stream in streams:
        LOGGER.info('Syncing %s', stream.name)
        STATE["this_stream"] = stream.name
        stream.sync() # pylint: disable=not-callable
    STATE["this_stream"] = None
    singer.write_state(STATE)
    LOGGER.info("Sync completed")


def main():
    args = utils.parse_args(
        [
            "app_id",
            "api_token",
        ])

    CONFIG.update(args.config)

    if args.state:
        STATE.update(args.state)

    do_sync()


if __name__ == '__main__':
    main()
