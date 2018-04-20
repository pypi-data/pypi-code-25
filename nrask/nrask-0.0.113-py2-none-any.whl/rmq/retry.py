__all__ = ['retry']

def retry(channel, service, body, headers, settings, ack):
    try:
        assert headers['retry-count'] < settings['services'][service]['retry-count']
    except AssertionError:
        ack.set_result(True)
        return
    except KeyError:
        headers['retry-count'] = 1
    else:
        headers['retry-count'] += 1

    from nrask.rmq import BasicProperties
    channel.basic_publish(
        exchange=settings['exchange']['retry'],
        routing_key=settings['services'][service]['rk'],
        body=body,
        properties=BasicProperties(
            headers=headers
        )
    )
    ack.set_result(True)
