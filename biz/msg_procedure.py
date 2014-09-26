#coding:utf-8
#File: msg_procedure.py
#Auth: lixp(@500wan.com)
#Date: 2014-09-22 14:32:24
#Desc: 

import tornado.ioloop
import os,sys,copy

APP_PATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
sys.path.append(os.path.join(APP_PATH,'lib'))
import db_tools
from logger import Log

logger = Log().getLog()
#PUSH_KEY_IOS = "apns.prod.push.rabbit"
#PUSH_KEY_AND = "android_push_" 
PUSH_KEY_IOS = "test_ios_apns"
PUSH_KEY_AND = "test_and_"

def process(evt):
    global R 
    R = db_tools.get_redis("msg")

    if evt.is_multi():
        logger.info("Begin to send a batch of msgs![ TOTAL:%d ]" % len(evt.u))
        multi_msg_proc(evt)
    else:
        logger.info("Begin to send a msg![ PUSHKEY:%s ]" % evt.u[0].get('pushkey'))
        single_msg_proc(evt)

def multi_msg_proc(evt):
    P = R.pipeline()
    for u in evt.u:
        """识别设备类型"""
        pushkey = u.get('pushkey')
        dev = evt.get_device(pushkey)
        if not dev:
            logger.error("Unknown device![ PUSHKEY:%S ]" % pushkey)
            continue

        """开关过滤"""
        pass

        body = evt.b
        if dev == "IOS":
            body = evt.b.replace('TOKEN', pushkey)
            key = PUSH_KEY_IOS
        elif dev == "ANDROID":
            key = PUSH_KEY_AND + pushkey
        P.rpush(key, body)
        logger.debug("MultiSend msg to redis![ KEY:%s MSG:%s ]" % (key, body))

    logger.info("MultiSend msg to redis![ TOTAL:%d ]" % P.__len__())
    P.execute()
        

def single_msg_proc(evt):
    """识别设备类型"""
    pushkey = evt.u[0].get('pushkey')
    dev = evt.get_device(pushkey)
    if not dev:
        logger.error("Unknown device![ PUSHKEY:%S ]" % pushkey)
        return 

    """开关过滤"""
    pass


    """写redis"""
    if dev == "IOS":
        evt.b = evt.b.replace('TOKEN', pushkey)
        key = PUSH_KEY_IOS
    elif dev == "ANDROID":
        key = PUSH_KEY_AND + pushkey
    R.rpush(key, evt.b)
    logger.info("SingleSend msg to redis![ KEY:%s MSG:%s ]" % (key, evt.b))
