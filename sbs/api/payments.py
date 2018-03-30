#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
import tornado
import tornado.escape
from tornado.gen import coroutine, Return
from tornado.web import HTTPError
from iap import AppStoreValidator, GooglePlayValidator, InAppValidationError
from iap.purchase import Purchase
from email.utils import formatdate
from orm import BaseModel
from orm.dbwrapper import _pairtext, _pairnum
import time
from datetime import datetime
import logging
import json

@coroutine
def process_record(user_id , purchases, status, platform, package):
    for purchase in purchases: 
        purchase_datetime = datetime.fromtimestamp(int(purchase.purchased_at) / 1000.0)
        sql = "INSERT INTO Payment SET %s,%s,%s,%s,%s,%s,%s,%s,%s ON DUPLICATE KEY UPDATE retry = retry + 1,status=%s" % (
                                           _pairtext("transaction_id", purchase.transaction_id),
                                           _pairtext("user_id", user_id),
                                           _pairtext("product_id", purchase.product_id),
                                           _pairnum("quantity", purchase.quantity),
                                           _pairtext("purchased_at", purchase_datetime.strftime("%Y-%m-%d %H:%M:%S")),
                                           _pairnum("status", status),
                                           _pairnum("retry", 0),
                                           _pairtext("platform", platform),
                                           _pairtext("package", package),
                                           status
                                          )
        result = yield BaseModel.execute_master(sql)
    yield BaseModel.cache_delete("SBS_PAYMENTS|%s" % (user_id))

@coroutine
def get(handler, *args, **kwargs):
    user_id = args[0]
    sql = "select * from Payment where user_id='%s' order by purchased_at desc"  % (user_id)
    result = yield BaseModel.select_master(sql)
    for r in result:
        r["purchased_at"] =  r["purchased_at"].strftime("%Y-%m-%d %H:%M:%S")
    raise Return((200, result))

@coroutine
def post(handler, *args, **kwargs):
    user_id = args[0]
    sbs_id = handler.request.headers.get("X-SBS-ID", "")
    apl    = handler.request.headers.get("X-Pitaya-Apl", "0")
    logging.info("%s %s %s " % (user_id, sbs_id, apl))
    for h in handler.request.headers.get_all():
        logging.info(h)
    logging.info(handler.request.body)
    data = tornado.escape.json_decode(handler.request.body)
    transaction_id = data.get("transactionid", u"")
    product_id = data.get("productid", u"")
    platform = handler.config.sbs.get(sbs_id,{}).get("platform", "")
    payment_conf = handler.config.payment.get(platform)

    #repeat order
    select_sql = "select 1 from Payment where transaction_id='%s' and status = 0 limit 1" % (transaction_id)
    select_result = yield BaseModel.select_master(select_sql)
    if select_result:
        raise Return((408, {"status": 408, "error": "[%s] repeat order [%s]" % (user_id, transaction_id)}))
    # unkonw platform type
    if not payment_conf:
        raise Return((407, {"status":407, "error" : "unknown platorm for payment %s" %(platform) }))
    result = {}

    if platform == "google":
        payload = json.loads(json.loads(data.get("receipt","")).get("Payload"))
        validator = GooglePlayValidator(payment_conf["app_id"], payment_conf["api_key"])
        result = (405,"")
        try:
            purchase = validator.validate(payload["json"], payload["signature"])
            yield process_record(user_id, purchase, 0, platform, payment_conf["app_id"])
            result = (200, {"transaction_id":purchase[0].transaction_id, "product_id":purchase[0].product_id, "purchased_at": purchase[0].purchased_at, "quantity": purchase[0].quantity})
        except Exception, e:
            purchase = [Purchase(transaction_id, product_id, 1, int(time.time() * 1000))]
            yield process_record(user_id, purchase, 1, platform, payment_conf["app_id"])
            logging.exception("[payment failed]%s %s %s %s %s " % (user_id, transaction_id, product_id, platform, str(e)))
            raise Return((405, {"status":405, "error":str(e)}))
        raise Return(result)

    elif platform == "ios":
        validator_prd = AppStoreValidator(payment_conf["app_id"], False)
        validator_sbx = AppStoreValidator(payment_conf["app_id"], True)

        try:
            try:
                purchase = yield validator_prd.validate(json.loads(data.get("receipt","")).get("Payload"))
            except:
                purchase = yield validator_sbx.validate(json.loads(data.get("receipt","")).get("Payload")) 

            yield process_record(user_id, purchase, 0,platform, payment_conf["app_id"])
            result = (200, {"transaction_id":purchase[0].transaction_id, "product_id":purchase[0].product_id, "purchased_at": purchase[0].purchased_at, "quantity": purchase[0].quantity})
        except Exception, e:
            purchase = [Purchase(transaction_id, product_id, 1, int(time.time() * 1000))]
            yield process_record(user_id, purchase, 1, platform, payment_conf["app_id"])
            logging.exception("[payment failed]%s %s %s %s %s " % (user_id, transaction_id, product_id, platform, str(e)))
            raise Return((405, {"status":405, "error":str(e)}))
        raise Return(result)

    raise Return((407, {"status":407, "error" : "unknown platorm for payment %s" %(platform) }))
