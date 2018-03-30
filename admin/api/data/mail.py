#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
from db import BaseModel
import logging

MAIL_LEN = 150
class Mail(BaseModel):
    seq_attrs = ["pkey","mail"]
    adv_seq_attrs = ["mail"]

    def __init__(self):
        super(Mail, self).__init__()
        self.mail = []

    def delete_old(self): 
        delete_old = False
        if len(self.mail) > MAIL_LEN:
            delete_old = True
        for mail_data in reversed(self.mail):
            if mail_data["opened"]:
                delete_old = False
                self.mail.remove(mail_data)
                break
        if delete_old:
            self.mail.pop()  
