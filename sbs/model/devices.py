#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
from orm import BaseModel
class Devices(BaseModel):
    seq_attrs = ["pkey", "device_id", "password", "oldpass", "game_center_id", "google_play_id","facebook_id"]
    def __init__(self):
        super(Devices, self).__init__()
        self.pkey = None
        self.device_id = ""
        self.password = ""
        self.oldpass = ""
        self.game_center_id = ""
        self.google_play_id = ""
        self.facebook_id = ""
