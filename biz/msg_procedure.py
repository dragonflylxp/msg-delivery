#coding:utf-8
#File: msg_procedure.py
#Auth: lixp(@500wan.com)
#Date: 2014-09-22 14:32:24
#Desc: 

import tornado.ioloop

APP_PATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
sys.path.append(os.path.join(APP_PATH,'lib'))
import db_tools

redis_conn = db_tools.get_redis("msg")

def process(evt, handler):
    if evt.is_multi():
        multi_msg_proc(evt.b, evt.u)
    else:
        single_msg_proc(evt.b,evt.u)
    data = {'a':'cxp'}
    ret  = handler.ok(data)
    tornado.ioloop.IOLoop.instance().add_callback(lambda: handler.finish(ret))


def single_msg_proc(msg, user):
    pass


def multi_msg_proc(msg, users):
    pass
