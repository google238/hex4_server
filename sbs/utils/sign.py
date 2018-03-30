#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
import hashlib
import hmac
import base64
import logging
import time
from email.utils import formatdate

REQUEST_SIGN_FORMAT = "%s\n%s\n%s\nx-sbs-date:%s\nx-sbs-id:%s\nx-sbs-user-id:%s\n%s"
RESPONSE_SIGN_FORMAT = "%s\n%s\n%s\nx-sbs-date:%s\n%s"

def makeReuestHeader(sbs_id , device_id, sbs_user_id, password, method, path, content_type = "", content = ""):
    content_md5 = hashlib.md5(content).hexdigest() if content else ""
    sbs_date = formatdate(timeval=None, localtime=False, usegmt=True)

    stringToSign = REQUEST_SIGN_FORMAT % (method.upper(),
                                          content_md5,
                                          content_type,
                                          sbs_date,
                                          sbs_id,
                                          sbs_user_id,
                                          path
                                         )
    signature_hex = hmac.new(str(password), str(stringToSign), hashlib.sha1).digest()
    signature = base64.b64encode(signature_hex)
    headers = {}
    headers["X-SBS-ID"] = sbs_id
    headers["X-SBS-USER-ID"] = sbs_user_id
    headers["X-SBS-DATE"] = sbs_date
    headers["Authorization"] = "SBS %s:%s" % (device_id, signature)
    return headers

def check_request(handler, password = ""):
    sbs_id = handler.request.headers.get("X-SBS-ID", "")
    is_admin = sbs_id in handler.config.sbs_admin
    is_normal =  sbs_id in handler.config.sbs

    if (not is_normal ) and (not is_admin):
        logging.error("wrong sbs_id %s" % (sbs_id))
        return False

    if handler.request.path.startswith("/devices") and handler.request.method.lower() == "post":
        return True

    auth_header = handler.request.headers.get("Authorization", None)
    if not auth_header:
        logging.error("no Authorization header")
        return False

    password = ""
    if handler.device:
        password = handler.device.password if not is_admin else  handler.config.sbs_admin[sbs_id]["admin_password"]

    if handler.request.path.startswith("/devices") and handler.request.method.lower() == "put":
        password = ""

    signature = auth_header.split(":")[1]
    content_type = handler.request.headers.get("Content-Type", None)
    content = handler.request.body
    content_md5, content_type = (hashlib.md5(content).hexdigest(), content_type) if content else ("", "")
    stringToSign = REQUEST_SIGN_FORMAT % (handler.request.method.upper(),
                                  content_md5,
                                  content_type,
                                  handler.request.headers.get("X-SBS-DATE", ""),
                                  sbs_id,
                                  handler.request.headers.get("X-SBS-USER-ID", ""),
                                  handler.request.path
                                 )

    signature_hex = hmac.new(str(password), str(stringToSign), hashlib.sha1).digest()
    client_signature = base64.b64encode(signature_hex)
    if client_signature != signature:
        logging.error("%s %s signature mismatch %s %s" % (client_signature, signature, password, stringToSign))
        return False
    return signature

def make_response(handler):
    sbs_id = handler.request.headers.get("X-SBS-ID", "")
    is_admin = sbs_id in handler.config.sbs_admin
    password = ""
    if handler.device:
        password = handler.device.password if not is_admin else handler.config.sbs_admin[sbs_id]["admin_password"]

    status = handler.get_status()
    sbs_date = formatdate(timeval=None, localtime=False, usegmt=True)
    content_md5, response_type = (hashlib.md5(handler.result).hexdigest(), "application/json") if handler.result else ("","")
    stringToSign = RESPONSE_SIGN_FORMAT % (status ,content_md5, response_type, sbs_date, handler.signature)
    if not handler.request.path.startswith("/devices"):
        signature_hex = hmac.new(str(password), str(stringToSign), hashlib.sha1).digest()
        response_signature = base64.b64encode(signature_hex)
        handler.set_header("X-Sbs-Signature", response_signature)
    if response_type:
        handler.set_header("Content-Type", response_type)
    handler.set_header("X-Sbs-Date", sbs_date)
    handler.set_header("X-Sbs-Status", "%s" %(handler.get_status()))
