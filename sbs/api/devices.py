#-*- coding: utf-8 -*-
"""
the devices module implements the device and user id generate logic
"""
from __future__ import absolute_import, division, print_function, with_statement
from tornado.gen import coroutine, Return
from model.master import Configs
from tornado.web import HTTPError
from utils import shortuuid
from model.devices import Devices
import tornado.escape
import logging

@coroutine
def post(handler, *args, **kwargs):
    """
    use shortuuid to generate unique ids and password for authorization
    method: POST
    url   : /devices
    response content type : application/json
    resonpse status code  : 200 : reponse body {
                                                 "device_id": "JNs8TbaVfbnyDznYliRSrelpTb3",
                                                 "user_id": "JNs8TbaVfbnyDznYliRSrelpTb3",
                                                 "password":"JNs8TbaVfbnyDznYliRSrelpTb3"
                                                }
    """
    user_id = shortuuid.uuid()
    device_id = shortuuid.uuid()
    password = shortuuid.uuid()

    device = Devices()
    device.pkey = user_id
    device.device_id = device_id
    device.password = password
    yield device.put()
    logging.info("post devices %s %s %s" %(device_id, user_id, password))
    raise Return((200,
         {"device_id": device_id,
         "user_id": user_id,
         "password": password
         }))

@coroutine
def get(handler, *args, **kwargs):
    user_id = args[0]
    if not user_id:
        raise HTTPError(404, "user_id can not be null ")

    device = yield Devices.get(user_id)
    result = {}
    if device:
        result["device_id"] = device.device_id
        result["google_play_id"] = device.google_play_id
        result["game_center_id"] = device.game_center_id
        result["facebook_id"]    = device.facebook_id

    raise Return((200, result))

@coroutine
def put(handler, *args, **kwargs):
    """
    upload clieny user data to server and generate new password for client side
    method: PUT
    url   : /devices/{user_id}
    user_id : the client side user_id
    request body : {"device_id":"JNs8TbaVfbnyDznYliRSrelpTb3" ,
                    "password":"JNs8TbaVfbnyDznYliRSrelpTb3",
                    "google_play_id":"g07841440136021388667",
                    "game_center_id":"",
                    "facebook_id":""
                    }
    response content type : application/json
    resonpse status code  : 200 : reponse body {
                                                 "device_id": "JNs8TbaVfbnyDznYliRSrelpTb3",
                                                 "user_id": "JNs8TbaVfbnyDznYliRSrelpTb3",
                                                 "password":"JNs8TbaVfbnyDznYliRSrelpTb3"
                                                }
    """
    user_id = args[0]
    data = tornado.escape.json_decode(handler.request.body)
    device_id = data.get("device_id")
    password = data.get("password")
    google_play_id = data.get("google_play_id")
    game_center_id = data.get("game_center_id")
    facebook_id = data.get("facebook_id")

    if not user_id:
        raise HTTPError(404, "user_id can not be null ")

    device = yield Devices.get(user_id)
    if not device:
        device = Devices()
        device.pkey = user_id
        device.device_id = device_id
        device.password = shortuuid.uuid()
        device.google_play_id = google_play_id
        device.game_center_id = game_center_id
        device.facebook_id = facebook_id
        device.oldpass = password
        yield device.put()
    else:
        device.pkey = user_id
        device.device_id = device_id
        device.password = password
        if not device.google_play_id:
            device.google_play_id = google_play_id
        if not device.game_center_id:
            device.game_center_id = game_center_id
        if not device.facebook_id:
            device.facebook_id = facebook_id
        yield device.put()
        logging.info("put devices %s %s %s" %(device_id, user_id, device.password))

    raise Return((200, {"device_id": device_id,
                        "user_id": user_id,
                        "password": device.password
                       }
                ))
