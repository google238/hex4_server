import signal
import time
from tornado import gen
from tornado import ioloop
from tornado.options import define, options, parse_command_line
from orm import BaseModel
import logging
import msgpack
from model.devices import Devices
import tornado.escape
from utils.sbs import Sbs
from iap.purchase import Purchase

class Test(BaseModel):
    seq_attrs = ["pkey","name", "data"]
    adv_seq_attrs = ["data"]

    def __init__(self):
        super(Test, self).__init__()
        self.name = ""
        self.data = {}

@gen.coroutine
def test_db():
    a = yield Test.get("test")
    print(a)
    if not a :
        a = Test()
        a.pkey = "test"
        a.name = "aaaa"
        a.data = {"aaaa":1}
        yield a.put()
    a = yield Test.get("test")
    print(a)
    yield a.delete()

    a = yield Test.get("test")
    print(a)

    a = yield Test.get("test")
    print(a)

    a = yield Test.get("test")
    print(a)

    a = yield Test.get("test")
    print(a)

    a = yield Test.get("test")
    print(a)

    a = yield Test.get("test")
    print(a)

    a = yield Test.get("test")
    print(a)

    if not a :
        a = Test()
        a.pkey = "test"
        a.name = "aaaa"
        a.data = {"aaaa":1}
        yield a.put()
    a = yield Test.get("test")
    print(a)

@gen.coroutine
def test_sbs():
    from utils.sbs import Sbs
    #password  = "ahbezhxpnapdjljbeywqfnrkhstxtqpjfylpxabakocrecimzh"
    #user_id   = "hq87ojkohwzc"
    #device_id = "8ykwochcwbcx"
    #sbs_id    = "2hxovi4fpkxtk6ic6r65u4eq"
    password  = "7uvy1v7v0ychfhv1gvngk3zpdmz0jlequvuw45r9dbkwxb6"
    device_id = "8ykwochcwbcx"
    user_id   = ""
    sbs_id    = "4b0oypb57qmmfjt057jn4mbm"
    sbs = Sbs(sbs_id, user_id, device_id, password)
    bucket = "userData"

    result = yield sbs.getBucketData(bucket, "8jk3k9c9mryb")
    print(result)

    #result = yield sbs.getUserData("8jk3k9c9mryb")
    #print(result)

    #result = yield sbs.getUserPayments("8jk3k9c9mryb")
    #print(result)

    #result = yield sbs.getUserPaymentsDetails("8jk3k9c9mryb")
    #print(result)

    #result = yield sbs.get_social_bind("google_play", "g07841440136021388667")
    #print(result)

@gen.coroutine
def test_memcached():
    yield BaseModel.cache_set("test",{"dddd":[]})
    result = yield BaseModel.cache_get("test")
    print(result)
    yield BaseModel.cache_set("test",{"ssssss":[]})
    result = yield BaseModel.cache_get("test")
    print(result)

class Request(object):
    def __init__(self,method, path, body=None):
        self.headers = {"X-SBS-USER-ID" : "8jk3k9c9mryb",
                        "X-SBS-ID" : "7k9ifp0utpb97a8zrorfewbw",
                        }
        self.method = method
        self.path = path
        self.body = body

class Handler(object):
    def __init__(self, method, path, body=None):
        self.request = Request(method, path, body=body)
        password  = "7uvy1v7v0ychfhv1gvngk3zpdmz0jlequvuw45r9dbkwxb6"
        device_id = "8ykwochcwbcx"
        user_id   = ""
        sbs_id    = "4b0oypb57qmmfjt057jn4mbm"
        self.sbs_client = Sbs(sbs_id, user_id, device_id, password)
        self.request.method = method

@gen.coroutine
def request(method, path, body=None):
    handler = Handler(method, path, body)
    handler.device = yield Devices.get(handler.request.headers.get("X-SBS-USER-ID"))
    method = handler.request.method.lower()
    path_parts   = path.split("/")

    try:
        mod = __import__("api.%s" %(path_parts[1].lower()), globals(), locals(), [method], -1)
    except ImportError , e:
        mod = __import__("api.bucket", globals(), locals(), [method], -1)
        path_parts.insert(0, "bucket");

    api_func = getattr(mod, method)
    if api_func:
        status, response = yield api_func(handler, *path_parts[2:])
        result = None
        if status != 204:
            result = tornado.escape.json_encode(response)
    else:
        raise HTTPError(405)
    raise gen.Return(result)

@gen.coroutine
def test_api():
    """ 
    print("test bucket get......................................................")
    result = yield request("GET", "/userData/8jk3k9c9mryb")
    print(result)
    print("test bucket PUT......................................................")
    result = yield request("PUT","/userData/8jk3k9c9mryb", result)
    print(result)
    result = yield request("GET", "/userData/8jk3k9c9mryb")
    print(result)
    print("test devices post......................................................")
    result = yield request("POST", "/devices")
    print(result)
    print("test devices put......................................................")
    result = yield request("PUT", "/devices/8jk3k9c9mryb/", """{"google_play_id":"g07841440136021388667","password": "X3CTNAKqwcYWc39dxjLJce", "user_id": "8jk3k9c9mryb", "device_id": "WWrvpkKC6Smb6eH4chtPRZ"}""")
    print(result)

    print("test social delete......................................................")
    result = yield request("DELETE", "/social/google_play/g07841440136021388667")
    print(result)

    print("test social put......................................................")
    result = yield request("PUT", "/social/google_play/g07841440136021388667", """{"user_ids": ["8jk3k9c9mryb"]}""")
    print(result)

    print("test social get......................................................")
    result = yield request("GET", "/social/google_play/g07841440136021388667")
    print(result)

    print("test users post ......................................................")
    result = yield request("POST", "/users")
    print(result)

    print("test add payment record......................................................")
    from api.payments import process_record
    purchase = Purchase("test----2", "test", 1, int(time.time() * 1000))
    purchase
    result = yield process_record("8jk3k9c9mryb" , purchase , 0, "google", "com.wooga.sumikko_jp")
    print(result)

    print("test users get......................................................")
    result = yield request("GET", "/users/8jk3k9c9mryb/payments")
    print(result)
    """
    result = yield request("PUT", "/social/google_play/g07841440136021388667", """{"user_ids": ["d5yg5rkfu4pw"]}""")
    print(result)
define("host",  default="0.0.0.0", help="http server bind address", type=str)
define("port" , default=9090, help="http server listening port", type=int)
define("config" , default="ci", help="service mode [production, staging, ci]", type=str)

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

    ioloop.IOLoop.instance().run_sync(test_api)
    ioloop.IOLoop.instance().start()
