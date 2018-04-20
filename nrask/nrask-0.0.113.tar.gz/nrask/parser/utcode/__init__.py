# -*- coding: utf-8 -*-
from base64 import b64decode,b64encode
from rask.base import Base
from types import BooleanType,DictType,FloatType,IntType,ListType,LongType,NoneType,StringType,TupleType,UnicodeType

__all__ = ['UTCode']

class UTCode(Base):
    @property
    def decode_type(self):
        try:
            assert self.__decode_types
        except (AssertionError,AttributeError):
            self.__decode_types = {
                'b':self.decoder_bool,
                'd':self.decoder_dict,
                'f':self.decoder_float,
                'i':self.decoder_int,
                'l':self.decoder_list,
                'n':self.decoder_none,
                's':self.decoder_string,
                'u':self.decoder_unicode
            }
        except:
            raise
        return self.__decode_types
    
    @property
    def encode_types(self):
        try:
            assert self.__encode_types
        except (AssertionError,AttributeError):
            self.__encode_types = {
                BooleanType:self.encoder_bool,
                DictType:self.encoder_dict,
                FloatType:self.encoder_float,
                IntType:self.encoder_int,
                ListType:self.encoder_list,
                LongType:self.encoder_int,
                NoneType:self.encoder_none,
                StringType:self.encoder_string,
                TupleType:self.encoder_list,
                UnicodeType:self.encoder_unicode
            }
        except:
            raise
        return self.__encode_types

    def decode(self,_,future,result=None):
        try:
            assert _[:3] == 'ut:'
        except (AssertionError,TypeError):
            future.set_result(None)
            self.log.error('Invalid UTCode')
            return False
        except:
            raise
        
        def on_future(r):
            future.set_result(r.result()[0])
            return True

        self.ioengine.loop.add_callback(
            self.decode_type[_[3]],
            _=_[3:],
            f=self.ioengine.future(on_future)
        )
        return True

    def decoder_bool(self,_,f):
        f.set_result(([False,True][int(_[2])],_[3:]))
        return True

    def decoder_dict(self,_,f,r=None):
        try:
            assert _[:2] == 'd:'
        except:
            raise
        else:
            def on_end(result):
                f.set_result(result.result())
                return True

            self.ioengine.loop.add_callback(
                self.decoder_dict_consumer,
                _=_[2:],
                f=self.ioengine.future(on_end),
                r={}
            )
        return True

    def decoder_dict_consumer(self,_,f,r=None):
        try:
            assert _[0] == 'e'
        except AssertionError:
            k,_ = self.decoder_dict_key(_)

            def on_future(result):
                r[k] = result.result()[0]

                self.ioengine.loop.add_callback(
                    self.decoder_dict_consumer,
                    _=result.result()[1],
                    f=f,
                    r=r
                )
                return True
            
            self.ioengine.loop.add_callback(
                self.decode_type[_[0]],
                _=_,
                f=self.ioengine.future(on_future)
            )
        except:
            raise
        else:
            f.set_result((r,_[1:]))
        return True

    def decoder_dict_key(self,_):
        c = _.index(':')
        l = int(_[1:c])
        return (_[c+1:l+c+1],_[l+c+1:])

    def decoder_float(self,_,f):
        f.set_result(
            (
                float(_[_.index(':')+1:_.index('z')]),
                _[_.index('z')+1:]
            )
        )
        return True
    
    def decoder_int(self,_,f):
        f.set_result(
            (
                int(_[_.index(':')+1:_.index('e')]),
                _[_.index('e')+1:]
            )
        )
        return True

    def decoder_list(self,_,f,r=None):
        try:
            assert _[:2] == 'l:'
        except:
            raise
        else:
            def on_end(result):
                f.set_result(result.result())
                return True
            
            self.ioengine.loop.add_callback(
                self.decoder_list_consumer,
                _=_[2:],
                f=self.ioengine.future(on_end),
                r=[]
            )
        return True

    def decoder_list_consumer(self,_,f,r=None):
        try:
            assert _[0] == 'e'
        except AssertionError:
            def on_future(result):
                r.append(result.result()[0])

                self.ioengine.loop.add_callback(
                    self.decoder_list_consumer,
                    _=result.result()[1],
                    f=f,
                    r=r
                )
                return True

            self.ioengine.loop.add_callback(
                self.decode_type[_[0]],
                _=_,
                f=self.ioengine.future(on_future)
            )
        except:
            raise
        else:
            f.set_result((r,_[1:]))
        return True    

    def decoder_none(self,_,f):
        f.set_result((None,_[3:]))
        return True
    
    def decoder_string(self,_,f):
        c = _.index(':')
        l = int(_[1:c])
        f.set_result((_[c+1:l+c+1],_[l+c+1:]))
        return True

    def decoder_unicode(self,_,f):
        c = _.index(':')
        l = int(_[1:c])
        f.set_result((b64decode(_[c+1:l+c+1]).decode('utf-8'),_[l+c+1:]))
        return True
    
    def encode(self,_,future,result=None):
        def on_future(r):
            result = ['ut:']
            result.append(r.result())
            future.set_result(''.join(result))
            return True
        
        self.ioengine.loop.add_callback(
            self.encode_types[type(_)],
            _=_,
            f=self.ioengine.future(on_future)
        )
        return True

    def encoder_bool(self,_,f):
        f.set_result('b:%s' % [0,1][_])
        return True
    
    def encoder_dict(self,_,f,i=None,r=None):
        try:
            k = i.next()
        except AttributeError:
            self.ioengine.loop.add_callback(
                self.encoder_dict,
                _=_,
                f=f,
                i=iter(_),
                r=['d:']
            )
        except StopIteration:
            r.append('e')
            f.set_result(''.join(r))
            return True
        except:
            raise
        else:
            def on_future(result):
                r.append('k%s:%s' % (len(k),k))
                r.append(result.result())

                self.ioengine.loop.add_callback(
                    self.encoder_dict,
                    _=_,
                    f=f,
                    i=i,
                    r=r
                )
                return True

            self.ioengine.loop.add_callback(
                self.encode_types[type(_[k])],
                _=_[k],
                f=self.ioengine.future(on_future)
            )
        return None

    def encoder_float(self,_,f):
        f.set_result('f:%sz' % _)
        return True
    
    def encoder_list(self,_,f,i=None,r=None):
        try:
            k = i.next()
        except AttributeError:
            self.ioengine.loop.add_callback(
                self.encoder_list,
                _=_,
                f=f,
                i=iter(_),
                r=['l:']
            )
        except StopIteration:
            r.append('e')
            f.set_result(''.join(r))
            return True
        except:
            raise
        else:
            def on_future(result):
                r.append(result.result())

                self.ioengine.loop.add_callback(
                    self.encoder_list,
                    _=_,
                    f=f,
                    i=i,
                    r=r
                )
                return True
            
            self.ioengine.loop.add_callback(
                self.encode_types[type(k)],
                _=k,
                f=self.ioengine.future(on_future)
            )
        return None

    def encoder_int(self,_,f):
        f.set_result('i:%se' % _)
        return True

    def encoder_none(self,_,f):
        f.set_result('n:e')
        return True
    
    def encoder_string(self,_,f):
        f.set_result('s%s:%s' % (len(_),_))
        return True
    
    def encoder_unicode(self,_,f):
        b = b64encode(_.encode('utf-8'))
        f.set_result('u%s:%s' % (len(b),b))
        return True

