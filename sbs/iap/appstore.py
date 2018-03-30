import tornado
from iap.purchase import Purchase
from iap.errors import InAppValidationError
from tornado.gen import coroutine, Return
from tornado.escape import json_decode, json_encode
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import logging

api_result_ok = 0
api_result_errors = {
    21000: InAppValidationError('Bad json'),
    21002: InAppValidationError('Bad data'),
    21003: InAppValidationError('Receipt authentication'),
    21004: InAppValidationError('Shared secret mismatch'),
    21005: InAppValidationError('Server is unavailable'),
    21006: InAppValidationError('Subscription has expired'),
    21007: InAppValidationError('Sandbox receipt was sent to the production env'),
    21008: InAppValidationError('Production receipt was sent to the sandbox env'),
}

class AppStoreValidator(object):

    def __init__(self, bundle_id, sandbox=False):
        self.bundle_id = bundle_id

        if sandbox:
            self.url = 'https://sandbox.itunes.apple.com/verifyReceipt'
        else:
            self.url = 'https://buy.itunes.apple.com/verifyReceipt'

    @coroutine
    def validate(self, receipt):
        receipt_json = {'receipt-data': receipt}
        try:
            http_client = tornado.httpclient.AsyncHTTPClient()
            http_response = yield http_client.fetch(self.url, method='POST', body = json_encode(receipt_json))
            api_response = json_decode(http_response.body)
        except Exception as e:
            logging.exception(str(e))
            raise InAppValidationError('HTTP error')

        status = api_response['status']
        if status != api_result_ok:
            error = api_result_errors.get(status, InAppValidationError('Unknown API status'))
            raise error

        receipt = api_response['receipt']
        purchases = self._parse_receipt(receipt)
        raise Return(purchases)

    def _parse_receipt(self, receipt):
        if 'in_app' in receipt:
            return self._parse_ios7_receipt(receipt)
        return self._parse_ios6_receipt(receipt)

    def _parse_ios6_receipt(self, receipt):
        if receipt['bid'] and self.bundle_id != receipt['bid']:
            raise InAppValidationError('Bundle id mismatch')
        return [Purchase.from_app_store_receipt(receipt)]

    def _parse_ios7_receipt(self, receipt):
        if self.bundle_id != receipt['bundle_id']:
            raise InAppValidationError('Bundle id mismatch')
        return [Purchase.from_app_store_receipt(r) for r in receipt['in_app']]
