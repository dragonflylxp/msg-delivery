#coding:utf-8
#File: main.py
#Auth: lixp(@500wan.com)
#Date: 2014-09-19 17:13:40
#Desc: 


import tornado.ioloop
import tornado.web

import os,sys
import getopt
import ujson

APP_PATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
sys.path.append(os.path.join(APP_PATH,'biz'))
sys.path.append(os.path.join(APP_PATH,'lib'))
import msg_procedure
import timer_procedure
import db_tools
from events import msgEvent 
from Cfg    import CFG


class MainHandler(tornado.web.RequestHandler):
    #初始化
    def initialize(self, timer):
        self.timer = timer

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

        #允许与当前时间一定误差范围内的事件为实时消息 

        #MSG LOOP
        if evt.is_now():
            msg_procedure.process(evt, self)     #实时消息
        else:
            self.timer.send(evt)
            #timer_procedure.process(evt, self.t)   #定时消息
        

def init_application(conf_file):
    confs = CFG.get_instance()
    confs.load_conf(conf_file)
    db_tools.set_up(confs.get())

def Usage():
    print u'''使用参数启动:
                usage: [-p|-c
                -p [prot] ******启动端口
                -c <file> ******加载配置文件
            '''
    sys.exit(0)

if __name__ == "__main__":
    #init
    port = 8776
    includes = None
    opts, argvs = getopt.getopt(sys.argv[1:], "c:p:h")
    for op, value in opts:
        if op == '-c':
            includes = value
        elif op == '-p':
            port = int(value)
        elif op == '-h':
            Usage()
    if not includes:
        Usage()
    confs       = init_application(includes)

    #启动timer线程
    t = timer_procedure.msgTimer()
    t.setDaemon(True)
    t.start()

    #main
    application = tornado.web.Application([(r"^/([^\.|]*)(?!\.\w+)$",MainHandler),dict(timer=t)])
    application.listen(port) 
    tornado.ioloop.IOLoop.instance().start()
