#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
from db import BaseModel
import logging

class Level(BaseModel):
    seq_attrs = ["pkey","stars","score","other"]
    adv_seq_attrs = ["other"]

    def __init__(self):
        super(Level, self).__init__()
        self.stars = 0
        self.score = 0
        self.other = {}
