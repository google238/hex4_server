#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
import tornado.escape
from tornado.gen import coroutine, Return
from utils import shortuuid
from orm import BaseModel
@coroutine
def post(handler, *args, **kwargs):
    """
    create new user for device and response the new user_id to client
    method: POST
    url   : /users
    response content type : application/json
    resonpse status code  : 200 : reponse body {"user_id": "JNs8TbaVfbnyDznYliRSrelpTb3"}
    """
    if not handler.device:
        raise Return((404, {"status":404, "error" : "X-SBS-USER-ID not found"}))
    user_id = shortuuid.uuid()
    handler.device.pkey = user_id
    yield handler.device.put()
    raise Return((200, {"user_id" : user_id}))

@coroutine
def get(handler, *args, **kwargs):
    """
    get user datas
    method: GET
    url   : /users/{user_id}/{data_type}
    response content type : application/json
    resonpse status code  : 200 : reponse body {
                              "payments": {
                                "ios": [
                                  {
                                    "id": "string",
                                    "date": "string",
                                    "package": "string"
                                  }
                                ],
                                "google": [
                                  {
                                    "id": "string",
                                    "date": "string",
                                    "package": "string"
                                  }
                                ],
                                "facebook": [
                                  {
                                    "id": "string",
                                    "date": "string",
                                    "package": "string"
                                  }
                                ]
                              }
                            }
    """
    user_id = args[0]
    data_type = args[1]
    if not user_id:
        raise Return((404, {"status":404, "error" : "user_id %s not found" % (user_id)}))
    if data_type =="payments":
        result = yield BaseModel.cache_get("SBS_PAYMENTS|%s" % (user_id), {})
        if not result:
            rows = yield BaseModel.select_master("select product_id, purchased_at, package , platform from Payment where user_id ='%s'" % (user_id))
            result = {"payments": {"ios":[], "google":[], "facebook": []}}
            for row in rows:
                result["payments"][row["platform"]].append({"id": row["product_id"], "date": row["purchased_at"].strftime("%Y-%m-%d %H:%M:%S") ,"package": row["package"]})
            yield BaseModel.cache_set("SBS_PAYMENTS|%s" % (user_id),result )
        raise Return((200, result))
    raise Return((404, {"status":404, "error" : "data_type %s not found" % (data_type)}))
