from rask.base import Base
from rask.parser.utcode import UTCode

__all__ = [
    'File'
]

class File(Base):
    @property
    def utcode(self):
        try:
            assert self.__utcode
        except (AssertionError,AttributeError):
            self.__utcode = UTCode()
        except:
            raise
        return self.__utcode
        
    def __consumer__(self,io,on_line,future):
        try:
            def on_decode(_):
                self.ioengine.loop.add_callback(
                    on_line,
                    _.result()
                )
                return True
            
            self.utcode.decode(
                io.next(),
                future=self.ioengine.future(on_decode)
            )           
        except StopIteration:
            future.set_result(True)
            return True
        except:
            raise
        else:
            self.ioengine.loop.add_callback(
                self.__consumer__,
                io=io,
                on_line=on_line,
                future=future
            )
        return None

    def close(self,io):
        try:
            io.close()
        except:
            return False
        return True
    
    def consumer(self,filename,on_line,future):
        try:
            io = self.open(filename)
            assert io
        except AssertionError:
            self.log.error('file (%s) not found!' % filename)
            future.set_result(False)
        except:
            raise
        else:
            def on_consumer(_):
                self.close(io)
                future.set_result(True)
                return True
            
            self.ioengine.loop.add_callback(
                self.__consumer__,
                io=io,
                on_line=on_line,
                future=self.ioengine.future(on_consumer)
            )
        return True

    def open(self,filename,flag='r'):
        try:
            io = open(filename,flag)
        except IOError:
            self.log.error('IOError (%s)!' % filename)
            return False
        except:
            raise
        return io

    def write(self,io,line,future):
        def on_encode(_):
            io.write(_.result())
            io.write('\n')
            future.set_result(True)
            return True
        
        self.utcode.encode(
            line,
            future=self.ioengine.future(on_encode)
        )
        return True
