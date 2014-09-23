#coding:utf-8
#File: events.py
#Auth: lixp(@500wan.com)
#Date: 2014-09-22 14:02:50
#Desc: 


class msgEvent(object):
    
    def __init__(self):
        """
            消息发送时间:POSIX(Unix) timestamp
            若为即时发送消息，则t=-1
        """
        self.t = '-1'     


        """消息体: MSG() """
        self.b = None


        """发送对象，USER() """
        self.u = None

    def from_dict(self, d):
        self.t = d.get('t', '-1')
        self.b = d.get('b', None)
        self.u = d.get('u', None)
        return self


    def set_now(self):
        self.t = '-1'

    def is_now(self):
        return self.t == '-1'

    def is_multi(self):
        pass


class MSG(object):
    def __init__(self):
        pass




class USER(object):
    def __init__(self):
        pass
