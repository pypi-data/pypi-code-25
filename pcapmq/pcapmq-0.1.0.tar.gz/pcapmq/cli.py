# -*- coding: utf-8 -*-

"""Console script for pcapmq."""
import sys
import logging
import asyncio
import click

import pcap
import dpkt
import ipaddress
from hbmqtt.client import MQTTClient, ClientException


@asyncio.coroutine
def uptime_coro(broker_url):
    client = MQTTClient()
    yield from client.connect(broker_url)
    return client


@asyncio.coroutine
def downtime_coro(client):
    yield from client.disconnect()


@click.command()
@click.option('--interface', default=None, help="Name of network interface, "
                                                "default use the first "
                                                "interface.")
@click.option('--filter', default="udp or arp", help="PCAP filter. Default is"
                                                " 'udp or arp'. Use 'ether "
                                                "src xx:xx:xx:xx:xx:xx' to "
                                                "track down particular device")
@click.option('--topic', default="pcapmq/result", help="MQTT topic. Default "
                                                       " is pcapmq/result")
@click.option('--broker-url', default=None, help="MQTT broker url")
@click.option('--payload-format', default="{} {}", help="MQTT payload format. "
                                                        "Default is '{} {}'")
def main(interface, filter, topic, broker_url, payload_format):
    """Send PCAP result to MQTT broker"""
    
    if broker_url:
        client = asyncio.get_event_loop().run_until_complete(uptime_coro(broker_url))
        click.echo("connected to MQTT broker")
    else:
        click.echo("no MQTT broker specified")      

    sniffer = pcap.pcap(name=interface, promisc=True,
                        timeout_ms=50, immediate=True)
    sniffer.setfilter(filter)
    decode = {
        pcap.DLT_LOOP: dpkt.loopback.Loopback,
        pcap.DLT_NULL: dpkt.loopback.Loopback,
        pcap.DLT_EN10MB: dpkt.ethernet.Ethernet
    }[sniffer.datalink()]
    
    click.echo("listening on %s: %s" % (sniffer.name, sniffer.filter))

    try:
        for timestamp, packet in sniffer:
            decoded_packet = decode(packet)
            message = payload_format.format(timestamp, decoded_packet)
            if client:
                asyncio.get_event_loop().run_until_complete(client.publish(topic, message.encode()))
            click.echo(message)

    except KeyboardInterrupt:
        pass

    finally:
        received, dropped, dropped_by_interface = sniffer.stats()
        click.echo("\n%d packets received by filter" % received)
        click.echo("%d packets dropped by kernel" % dropped)
        click.echo("%d packets dropped by interface" %
                   dropped_by_interface)
        if client:
            asyncio.get_event_loop().run_until_complete(downtime_coro(client))
            click.echo("disconnected from MQTT broker")

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pylint: disable=no-value-for-parameter
