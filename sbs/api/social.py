#-*- coding: utf-8 -*-
"""
scolial module implment the social interfaces, client side can use these interfaces to:
1. get the bind info of social network
2. connect user_id to social nertwork id
3. delete social network id binding of user_id
"""
from __future__ import absolute_import, division, print_function, with_statement
import tornado.escape
from tornado.web import HTTPError
from tornado.gen import coroutine, Return
from utils.sbs import Sbs
from model.social import GooglePlayBind, GameCenterBind, FacebookBind
from model.devices import Devices

# register the social provider binding model classes with the provider name
_SocialBindClasses = {}
_SocialBindClasses["facebook"]    = FacebookBind
_SocialBindClasses["google_play"] = GooglePlayBind
_SocialBindClasses["game_center"] = GameCenterBind

@coroutine
def get(handler, *args, **kwargs):
    """
    get the bind info of social network by social id
    method: GET
    url   : /social/{provider}/{social_id}
    provider : the privider name it may be "google_play" ,"game_center", "facebook"
    socail_id : the social network player id
    response content type : application/json
    resonpse status code  : 200 : reponse body {"user_ids": ["JNs8TbaVfbnyDznYliRSrelpTb3"]}
                            404 : no resopnse body , No user could be found for the given user_id
    """
    # get parameters
    provider = args[0]
    social_id = args[1]

    # check sbs data
    BindClass = _SocialBindClasses[provider]
    bind = yield BindClass.get(social_id)
    user_ids = []
    if not bind:
        result = {"user_ids": []}
        if handler.sbs_client:
            result = yield handler.sbs_client.get_social_bind(provider, social_id)

        bind = BindClass()
        bind.pkey = social_id
        bind.user_ids = result["user_ids"]
        yield bind.put()

    user_ids = bind.user_ids

    if user_ids:
        raise Return((200, {"user_ids": user_ids}))

    raise HTTPError(404, "No user could be found for the given %s ID : %s" % (provider, social_id))

@coroutine
def put(handler, *args, **kwargs):
    """
    sync the local bind info of social_id to server
    method: PUT
    url   : /social/{provider}/{social_id}
    provider : the privider name it may be "google_play" ,"game_center", "facebook"
    socail_id : the social network player id
    request body : {"user_ids": [""JNs8TbaVfbnyDznYliRSrelpTb3""]}
    response content type : application/json
    resonpse status code  : 204 success no response body
                            403 reponse body {"status": 403, "error":"submitted_users_invalid"} ,
                                user ID must be included in the user_ids list
                            403 reponse body {"status": 403, "error":"user_already_connected"} ,
                                user id already connected to a different social id
                            412 reponse body {"user_ids" : "JNs8TbaVfbnyDznYliRSrelpTb3"} ,
                                another user has already been connected this social_id
    """
    # get parameters
    provider = args[0]
    social_id = args[1]
    data = tornado.escape.json_decode(handler.request.body)

    # check sbs data
    BindClass = _SocialBindClasses[provider]
    bind = yield BindClass.get(social_id)
    need_save = False
    if not bind:
        result = {"user_ids": []}
        if handler.sbs_client:
            try:
                result = yield handler.sbs_client.get_social_bind(provider, social_id)
            except:
                pass
        bind = BindClass()
        bind.pkey = social_id
        bind.user_ids = result["user_ids"]
        yield bind.put()

    # user ID must be included in the user_ids list
    if (not data) or (not data["user_ids"]):
        raise Return((403, {"status": 403, "error":"submitted_users_invalid"}))

    user_id = data["user_ids"][0]

    # another user has already been connected this social_id
    if len(bind.user_ids) > 0 and user_id not in bind.user_ids:
        raise Return((412, {"user_ids" : bind.user_ids}))

    # user id already connected to a different social id
    device = yield Devices.get(user_id)
    bind_id = getattr(device, "%s_id" % (provider)) if device else None
    if bind_id and bind_id != social_id:
        raise Return((403, {"status": 403, "error":"user_already_connected"}))

    # add current user_id to social_id binding
    if not device:
        device = Devices()
        device.pkey = user_id

    setattr(device, "%s_id" % (provider), social_id)
    yield device.put()

    if user_id not in bind.user_ids:
        bind.user_ids.append(user_id)
        yield bind.put()
    raise Return((204, None))

@coroutine
def delete(handler, *args, **kwargs):
    """
    get the bind info of social network by social id
    method: DELETE
    url   : /social/{provider}/{social_id}
    provider : the privider name it may be "google_play" ,"game_center", "facebook"
    socail_id : the social network player id
    response content type : application/json
    resonpse status code  : 204 success no response body
                            404 reponse body {"status": 404, "error":"unknown_social_id"} ,
                                no user could be found for the given social id
                            404 reponse body {"status": 404, "error":"unknown_association"} ,
                                the user is not associated with that social id
    """
    provider = args[0]
    social_id = args[1]
    user_id = handler.request.headers.get("X-SBS-USER-ID","")

    # check sbs data
    BindClass = _SocialBindClasses[provider]
    bind = yield BindClass.get(social_id)
    need_save = False
    if not bind:
        result = {"user_ids": []}
        if handler.sbs_client:
            try:
                result = yield handler.sbs_client.get_social_bind(provider, social_id)
            except:
                pass
    
        bind = BindClass()
        bind.pkey = social_id
        bind.user_ids = result["user_ids"]
        yield bind.put()

    # no user could be found for the given social id
    if not bind.user_ids:
        raise Return((404, {"status": 404, "error":"unknown_social_id"}))

    # the user is not associated with that social id
    if user_id not in bind.user_ids:
        raise Return((404, {"status": 404, "error":"unknown_association"}))

    # remove the user_id wassociated with social id
    bind.user_ids.remove(user_id)
    yield bind.put()

    raise Return((204, None))
