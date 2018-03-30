#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
from db import BaseModel
import logging

class RewardCode(BaseModel):
   seq_attrs = ["pkey","boxid", "uid"]
   adv_seq_attrs = []

   def __init__(self):
       super(RewardCode, self).__init__()
       self.pkey= ""
       self.uid= ""
       self.boxid = ""
