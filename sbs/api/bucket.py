#-*- coding: utf-8 -*-
"""
this file implements the KV store service operations
"""
from __future__ import absolute_import, division, print_function, with_statement
import tornado.escape
from tornado.gen import coroutine, Return
from model.bucket import Bucket
from utils.sbs import Sbs
import logging

@coroutine
def get(handler, *args, **kwargs):
    """
    for a single user_id, get the value stored in a custom bucket
    method: GET
    url   : /{bucket}/{user_id}
    bucket : the bucket name
    user_id : user id
    response content type : application/json
    resonpse status code  : 200 success response body json data
    """
    bucket_id = args[0]
    user_id = args[1]
    BucketClasss = type("Bucket_%s" % (bucket_id), (Bucket,), {})
    bucket = yield BucketClasss.get(user_id)
    result = {}
    if bucket:
        result = bucket.data
    elif handler.sbs_client:
        try:
            result = yield handler.sbs_client.getBucketData(bucket_id, user_id)
        except Exception, e:
            logging.info(str(e))  
          
    if not bucket:        
        bucket = BucketClasss()
        bucket.pkey = user_id
        bucket.data = result
        yield bucket.put()

    if not bucket.data:
        raise Return((404, result))

    raise Return((200, result))

@coroutine
def put(handler, *args, **kwargs):
    """
    updates data for a given user_id in a custom bucket
    method: PUT
    url   : /{bucket}/{user_id}
    bucket : the bucket name
    user_id : user id
    request body : a json data
    response content type : application/json
    resonpse status code  : 204 success, 405 server version is bigger
    """
    bucket_id = args[0]
    user_id = args[1]
    content = tornado.escape.json_decode(handler.request.body)
    BucketClasss = type("Bucket_%s" % (bucket_id), (Bucket,), {})
    bucket = yield BucketClasss.get(user_id)
    if not bucket:
        bucket = BucketClasss()
        bucket.pkey = user_id 
    if bucket_id == "userData":
       save_ver = int(content.get("data", {}).get("saveVer",0))
       current_ver = int(bucket.data.get("data", {}).get("saveVer",0))
       if save_ver < current_ver:
           raise Return((405, None))
    bucket.data = content 
    yield bucket.put()
    raise Return((204, None))

@coroutine
def get_bucket(bucket_id , user_id):
    BucketClasss = type("Bucket_%s" % (bucket_id), (Bucket,), {})
    bucket = yield BucketClasss.get(user_id)
    result = {}
    if bucket:
        result = bucket.data
    raise Return(result)

@coroutine
def put_bucket(bucket_id, user_id, data):
    content = tornado.escape.json_decode(data)
    BucketClasss = type("Bucket_%s" % (bucket_id), (Bucket,), {})
    bucket = yield BucketClasss.get(user_id)
    if not bucket:
        bucket = BucketClasss()
        bucket.pkey = user_id 
    bucket.data = content 
    yield bucket.put()
    raise Return(bucket.data)
