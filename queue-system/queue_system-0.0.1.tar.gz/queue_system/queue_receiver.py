import pika


class QueueReceiver:
    def __init__(self, queue_name, host, port, callback):
        self.parameters = pika.ConnectionParameters(host=host, port=port)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.queue_name = queue_name
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.callback = callback

    def startListener(self):
        self.channel.basic_consume(self.callback, queue=self.queue_name)
        try:
            print("[*] Waiting for messages!")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.connection.close()
