# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
import time
import zmq
import logging
from zmq.log.handlers import PUBHandler
from tornado.process import cpu_count
from tornado.options import define, options, parse_command_line

def start_stats(root_topic = "snowpear"):
    context = zmq.Context(cpu_count()) 
    pub = context.socket(zmq.PUB)
    pub.bind(options.stats_endpoint)
    handler = PUBHandler(pub)
    handler.root_topic = root_topic
    logger = logging.getLogger()
    logger.addHandler(handler)

def stats_log(topic, msg):
    msg = zmq.log.handlers.TOPIC_DELIM.join([topic, msg])
    logging.info(msg)
    
define("stats_endpoint", default="tcp://*:1998", help="stats log publish endpoint", type=str)
