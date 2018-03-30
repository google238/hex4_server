#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

class Config(object):
    def __init__(self):
        super(Config, self).__init__()

    def configure(self, cfg_file):
        cf = open(cfg_file)
        try:
            gs = {}
            exec(cf.read(), gs)
            for k in gs:
                if k != "__builtins__":
                    setattr(self, k, gs[k])
        finally:
            cf.close()
