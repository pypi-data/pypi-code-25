from rask.base import Base
from rask.options import options

__all__ = ['Announce']

class Announce(Base):
    def __init__(self,channel,settings,future=None):
        self.channel = channel.result().channel
        self.future = future
        self.settings = settings
        self.ioengine.loop.add_callback(self.exchange_declare)
        self.log.info('started')

    def finish(self):
        try:
            self.future.set_result(True)
        except AttributeError:
            pass
        except:
            raise
        return True

    def exchange_declare(self):
        def on_topic(*args):
            self.log.info('Exchange declare: %s' % self.settings['exchange']['topic'])
            return True

        def on_headers(*args):
            self.log.info('Exchange declare: %s' % self.settings['exchange']['headers'])
            self.channel.exchange_bind(
                destination=self.settings['exchange']['headers'],
                source=self.settings['exchange']['topic'],
                routing_key='#'
            )
            self.ioengine.loop.add_callback(self.queue_declare)
            return True

        self.channel.exchange_declare(
            callback=on_topic,
            exchange=self.settings['exchange']['topic'],
            exchange_type='topic',
            durable=True
        )

        self.channel.exchange_declare(
            callback=on_headers,
            exchange=self.settings['exchange']['headers'],
            exchange_type='headers',
            durable=True
        )
        return True

    def queue_bind_header(self,service):
        try:
            assert 'bind_args' in self.settings['services'][service]
        except AssertionError:
            pass
        except:
            raise
        else:
            def log(*args):
                return self.queue_bind_log(
                    self.settings['exchange']['headers'],
                    self.settings['services'][service]['bind_args'],
                    self.settings['services'][service]['queue']
                )

            self.channel.queue_bind(
                arguments=self.settings['services'][service]['bind_args'],
                callback=log,
                exchange=self.settings['exchange']['headers'],
                queue=self.settings['services'][service]['queue'],
                routing_key=''
            )
        return True

    def queue_bind_log(self,e,b,q):
        self.log.info('Queue bind: %s -> %s -> %s' % (e,b,q))
        return True

    def queue_bind_rk(self,service):
        try:
            assert 'rk' in self.settings['services'][service]
        except AssertionError:
            pass
        except:
            raise
        else:
            def log(*args):
                return self.queue_bind_log(
                    self.settings['exchange']['topic'],
                    self.settings['services'][service]['rk'],
                    self.settings['services'][service]['queue']
                )

            self.channel.queue_bind(
                callback=log,
                exchange=self.settings['exchange']['topic'],
                queue=self.settings['services'][service]['queue'],
                routing_key=self.settings['services'][service]['rk']
            )
        return True

    def queue_declare(self,_=None):
        try:
            service = _.next()
        except AttributeError:
            self.ioengine.loop.add_callback(
                self.queue_declare,
                iter(self.settings['services'])
            )
        except StopIteration:
            self.ioengine.loop.add_callback(
                self.finish
            )
            return True
        except:
            raise
        else:
            def on_declare(*args):
                self.ioengine.loop.add_callback(self.queue_bind_header,service)
                self.ioengine.loop.add_callback(self.queue_bind_rk,service)

                self.log.info('Queue declare: %s' % self.settings['services'][service]['queue'])
                self.ioengine.loop.add_callback(
                    self.queue_declare,
                    _=_
                )
                return True

            self.channel.queue_declare(
                arguments=self.settings['services'][service].get('arguments'),
                auto_delete=self.settings['services'][service].get('auto_delete'),
                callback=on_declare,
                durable=self.settings['services'][service].get('durable',True),
                exclusive=self.settings['services'][service].get('exclusive',False),
                queue=self.settings['services'][service]['queue']
            )
        return None
