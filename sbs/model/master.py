#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
from orm import BaseModel
class Configs(BaseModel):
    seq_attrs = ["pkey", "data"]
    adv_seq_attrs = ["data"]

    def __init__(self):
        super(Configs, self).__init__()
        self.data = {}
