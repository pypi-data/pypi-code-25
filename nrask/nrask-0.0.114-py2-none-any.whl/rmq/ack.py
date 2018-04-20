__all__ = ['ack']

def ack(channel,method):
    def f(_):
        try:
            assert _ and _.result()
        except AssertionError:
            channel.basic_nack(method.delivery_tag)
            return False
        except AttributeError:
            pass
        except:
            raise
        
        channel.basic_ack(method.delivery_tag)
        return True
    return f
