#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
from db import BaseModel
import logging

class Friends(BaseModel):
   seq_attrs = ["pkey", "invitelist","acceptlist", "friends","hearts","code", "invited", "inviter","invite_gift"]
   adv_seq_attrs = ["invitelist","acceptlist", "friends", "hearts", "invited","invite_gift"]

   def __init__(self):
       super(Friends, self).__init__()
       self.code = ""
       self.invitelist = []
       self.acceptlist = []
       self.friends = []
       self.invited = []
       self.inviter = None
       self.hearts = {}
       self.invite_gift = {}

class FacebookFriends(BaseModel):
   seq_attrs = ["pkey", "friends"]
   adv_seq_attrs = ["friends"]

   def __init__(self):
       super(FacebookFriends, self).__init__()
       self.friends = []
