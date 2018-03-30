#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
from orm import BaseModel
class AdminUser(BaseModel):
    seq_attrs = ["pkey", "password", "email", "permissions"]
    def __init__(self):
        super(AdminUser, self).__init__()
        self.pkey = None
        self.password = None
        self.email = ""
        self.permissions = ""
