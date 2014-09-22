#coding:utf-8
#File: main.py
#Auth: lixp(@500wan.com)
#Date: 2014-09-19 17:13:40
#Desc: 


import tornado.ioloop
import tornado.web

import os,sys
import ujson
APP_PATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
sys.path.append(os.path.join(APP_PATH,'biz'))
sys.path.append(os.path.join(APP_PATH,'lib'))
import msg_procedure
#import timer_procedure
from events import msgEvent 

class MainHandler(tornado.web.RequestHandler):
    """
    #初始化
    def initialize(self, d):
        pass
    """

    #预处理
    def prepare(self):
        pass


    #后处理
    def ok(self, data):
        resp = ujson.dumps({'resp':data}, ensure_ascii=False)
        return resp

    """
    query_arguments   : dict(querystring)
    body_arguments    : dict(body)
    arguments         : dict(querystring+body)
    """
    #@tornado.web.asynchronous
    def get(self, path):
        self.write(self.request.query_arguments)

    @tornado.web.asynchronous
    def post(self, path):

        #RCVD MSG EVENT
        d = dict((k, v[-1]) for k, v in self.request.body_arguments.iteritems()) 
        evt = msgEvent().from_dict(d)

        #MSG LOOP
        if evt.is_now():
            msg_procedure.process(evt, self)     #实时消息
        else:
            self.write("else")
        #    timer_procedure.process(evt, self)   #定时消息

        
        
#正则提取url参数
application = tornado.web.Application([(r"^/([^\.|]*)(?!\.\w+)$",MainHandler),])

if __name__ == "__main__":
    application.listen(8776)
    tornado.ioloop.IOLoop.instance().start()
    
