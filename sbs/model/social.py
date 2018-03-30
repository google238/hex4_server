#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
from orm import BaseModel

class GooglePlayBind(BaseModel):
    seq_attrs = ["pkey", "user_ids"]
    adv_seq_attrs = ["user_ids"]
    def __init__(self):
        super(GooglePlayBind, self).__init__()
        self.pkey = None
        self.user_ids = []

class GameCenterBind(BaseModel):
    seq_attrs = ["pkey", "user_ids"]
    adv_seq_attrs = ["user_ids"]
    def __init__(self):
        super(GameCenterBind, self).__init__()
        self.pkey = None
        self.user_ids = []

class FacebookBind(BaseModel):
    seq_attrs = ["pkey", "user_ids"]
    adv_seq_attrs = ["user_ids"]
    def __init__(self):
        super(FacebookBind, self).__init__()
        self.pkey = None
        self.user_ids = []
