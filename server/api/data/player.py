#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
from db import BaseModel
import logging

class Player(BaseModel):
    seq_attrs = ["pkey","name","fbname","avatar", "banner", "fb_id", "stars", "level", "recieve_heart", "system_mail"]
    adv_seq_attrs = ["system_mail"]

    def __init__(self):
        super(Player, self).__init__()
        self.name = ""
        self.fbname = ""
        self.fb_id  = ""
        self.avatar = ""
        self.banner = ""
        self.stars = 0
        self.level = 0
        self.recieve_heart = 1
        self.system_mail = []

class Checkin(BaseModel):
    seq_attrs = ["pkey","data"]
    adv_seq_attrs = ["data"]

    def __init__(self):
        super(Checkin, self).__init__()
        self.data = {}

class CheckinEvent(BaseModel):
    seq_attrs = ["pkey","data"]
    adv_seq_attrs = ["data"]

    def __init__(self):
        super(CheckinEvent, self).__init__()
        self.data = {}
        

class FBIdBind(BaseModel):
    seq_attrs = ["pkey","sbs_user_id"]
    adv_seq_attrs = []

    def __init__(self):
        super(FBIdBind, self).__init__()
        self.sbs_user_id  = ""

class DeviceBind(BaseModel):
    seq_attrs = ["pkey","device_id"]
    adv_seq_attrs = []
    
    def __init__(self):
        super(DeviceBind, self).__init__()
        self.device_id  = ""

class Ruby(BaseModel):
    seq_attrs = ["pkey","list"]
    adv_seq_attrs = ["list"]
    def __init__(self):
        super(Ruby, self).__init__()
        self.list = []

class Finance(BaseModel):
    seq_attrs = ["pkey","source",
                 "total_gold", "total_free_gold", "total_pay_gold",
                 "gold", "free_gold", "pay_gold", 
                 "total_ruby", "total_free_ruby", "total_pay_ruby",
                 "ruby", "free_ruby", "pay_ruby"]
    adv_seq_attrs = []

    def __init__(self):
        super(Finance, self).__init__()
        self.total_gold = 0
        self.source = ''
        self.total_free_gold = 0
        self.total_pay_gold = 0
        self.total_ruby = 0
        self.total_free_ruby = 0
        self.total_pay_ruby = 0 
        self.gold = 0
        self.free_gold = 0
        self.pay_gold = 0
        self.ruby = 0
        self.free_ruby = 0
        self.pay_ruby = 0
