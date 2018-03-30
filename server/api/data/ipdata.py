#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
from db import BaseModel
import logging

class IPData(BaseModel):
   seq_attrs = ["pkey", "data"]
   adv_seq_attrs = ["data"]
   def __init__(self):
       super(IPData, self).__init__()
       self.data = {}
