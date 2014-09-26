#coding:utf-8
#File: events.py
#Auth: lixp(@500wan.com)
#Date: 2014-09-22 14:02:50
#Desc: 

import ujson

"""
    业务端接口：
        t : 1.支持POSIX(Unix) timestamp; 2.日期(未支持), -1表示实时消息
        b : 消息体，string(json.dumps),分发系统不关心消息内容
        u : 发送对象，[{'pushkey':xxx,'username':xxx}, {}, {}, ...]
"""
class msgEvent(object):
    
    def __init__(self):
        self.t = '-1'     
        self.b = None
        self.u = None

    def from_dict(self, d):
        self.t = d.get('t', '-1')
        self.b = d.get('b', None)
        self.u = d.get('u', None)
        if not self.u:
            self.u = ujson.loads(self.u, ensure_ascii=False)
        return self

    """将定时消息转为实时消息"""
    def set_now(self):
        self.t = '-1'

    """判断是否为实时消息"""
    def is_now(self):
        return self.t == '-1'

    """判断是否为批量发送"""
    def is_multi(self):
        return len(self.u) > 1

    """判断device类型"""
    def get_device(self, pushkey):
        if not pushkey:
            return None
        if len(pushkey) == 64:
            return "IOS"
        return "ANDROID"

