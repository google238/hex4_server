import signal
import code
import time
from tornado import gen
from tornado import ioloop
from tornado.options import define, options, parse_command_line
import logging
import functools
from orm import BaseModel

def sync_wrapper_classmethod(wrapped_func):
    @functools.wraps(wrapped_func)
    def _w(*args, **kwargs):
        result = wrapped_func.__func__(*args, **kwargs)
        if not gen.is_future(result):
            return result

        @gen.coroutine
        def async_call():
            res = yield result
            raise gen.Return(res)
        return ioloop.IOLoop.current().run_sync(async_call)
    return classmethod(_w)

def sync_wrapper(wrapped_func):
    @functools.wraps(wrapped_func)
    def _w(*args, **kwargs):
        result = wrapped_func.__func__(*args, **kwargs)
        if not gen.is_future(result):
            return result

        @gen.coroutine
        def async_call():
            res = yield result
            raise gen.Return(res)
        return ioloop.IOLoop.current().run_sync(async_call)
    return _w

BaseModel.get = sync_wrapper_classmethod(BaseModel.get)
BaseModel.delete = sync_wrapper(BaseModel.delete)
BaseModel.put = sync_wrapper(BaseModel.put)
BaseModel.cache_get = sync_wrapper_classmethod(BaseModel.cache_get)
BaseModel.cache_set = sync_wrapper_classmethod(BaseModel.cache_set)
BaseModel.cache_delete = sync_wrapper_classmethod(BaseModel.cache_delete)

def shell():
    code.interact(local=locals())

define("host",  default="0.0.0.0", help="http server bind address", type=str)
define("port" , default=9090, help="http server listening port", type=int)
define("config" , default="production", help="service mode [production, staging, ci]", type=str)

def shutdown():
    """ Stop server and add a callback to stop I/O loop"""
    try:
        io_loop = ioloop.IOLoop.instance()
        logging.info("Will shutdown in 2 seconds ...")
        io_loop.add_timeout(time.time() + 2, io_loop.stop)
    except Exception,e:
        logging.exception(str(e))

def sig_handler(sig,frame):
    """ Catch signals and callback"""
    ioloop.IOLoop.instance().add_callback(shutdown)

if __name__ == "__main__":
    parse_command_line()

    # add signal handler to stop server
    signal.signal(signal.SIGTERM , sig_handler)
    signal.signal(signal.SIGINT , sig_handler)
    shell()    
