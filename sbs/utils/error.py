#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

class SBSError(Exception):
    def __init__(self, status_code=500, message=None, *args, **kwargs):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return message
