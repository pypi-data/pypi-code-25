"""VirtuinTestPublisher is used to publish status updates over AMQP
(via RabbitMQ).
"""
import time
import pika


def openBroker(hostName, maxAttempts, delayms):
    """Open connection to RabbitMQ with retries
    Args:
        hostName (str): Address of broker
        maxAttempts (int): Number of attempts
        delayms (float): Delay before retry
    Returns:
        None
    """
    connParams = pika.ConnectionParameters(
        host=hostName,
        connection_attempts=1,
        socket_timeout=delayms/1000.
    )
    conn = None
    connErr = None
    for attempts in range(maxAttempts):
        try:
            conn = pika.BlockingConnection(connParams)
            return conn
        # pylint: disable=broad-except
        except Exception as err:
            connErr = err
            if attempts < (maxAttempts - 1):
                time.sleep(delayms/1000.)
    raise connErr or Exception('Failed connecting to rabbitmq broker')
