#coding:utf-8
#File: main.py
#Auth: lixp(@500wan.com)
#Date: 2014-09-19 17:13:40
#Desc: 


import tornado.ioloop
import tornado.web
from tornado.log import access_log, gen_log

import os,sys
import getopt
import signal
import ujson

APP_PATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
sys.path.append(os.path.join(APP_PATH,'biz'))
sys.path.append(os.path.join(APP_PATH,'lib'))
import db_tools
import msg_procedure
import timer_procedure
from events import msgEvent 
from Cfg    import CFG
from logger import Log

class MainHandler(tornado.web.RequestHandler):

    def initialize(self, timer):
        self.timer = timer
        self.evt   = None

    def prepare(self):
        d = dict((k, v[-1]) for k, v in self.request.arguments.iteritems()) 
        d['u'] = []

        #解析file upload
        if self.request.files:
            hfile   = self.request.files['file'][0] 
            fstream = hfile.get('body')
            flines  = fstream.split('\n')
            for line in flines:
                if not line : continue
                [p, u]  = line.split('#') 
                d['u'].append({'pushkey':p, 'username':u})
        else:
            d['u'].append({'pushkey':d['pushkey'], 'username':d['username']})

        logger.debug("Receive a request![ DATA:%s ]" % ujson.dumps(d, ensure_ascii=False))
        self.evt = msgEvent().from_dict(d)

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
        pass

    @tornado.web.asynchronous
    def post(self, path):
        #MSG PROC 
        if self.evt.is_now():
            msg_procedure.process(self.evt)     #实时消息
        else:
            self.timer.process(self.evt)        #定时消息

        self.finish()
        
def init_application(conf_file):
    confs = CFG.get_instance()
    try:
        confs.load_conf(conf_file)
    except IOError,e:
        print e
        sys.exit(0)
        
    logfile = confs.get("Log/log_dir")
    Log.set_up(os.path.join(APP_PATH,logfile), confs.get("Log/logger"))
    global logger
    logger = Log().getLog()
    db_tools.set_up(confs.get())

def log_request(handler):
    """http日志函数
    """
    if handler.get_status() < 400:
        log_method = access_log.info
    elif handler.get_status() < 500:
        log_method = access_log.warning
    else:
        log_method = access_log.error
    req = handler.request
    log_method('"%s %s" %d %.6f',
               req.method, req.uri, 
               handler.get_status(),
               req.request_time() )

def Usage():
    print u'''使用参数启动:
                usage: [-p|-c
                -p [prot] ******启动端口
                -c <file> ******加载配置文件
            '''
    sys.exit(0)

def quit_app(*args):
    """信号处理，退出程序
    """
    tornado.ioloop.IOLoop.instance().stop()
    logger.info('Msg-delivery stopped!')

signal.signal(signal.SIGTERM, quit_app)
signal.signal(signal.SIGINT,  quit_app)
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
    confs = init_application(includes)
    logger.info("Msg-delivery initialized!")

    #main
    timer = timer_procedure.msgTimer()
    application = tornado.web.Application([(r"^/([^\.|]*)(?!\.\w+)$",MainHandler,dict(timer=timer)),], log_function=log_request)
    application.listen(port) 
    logger.info("Msg-delivery start to Loop!")
    tornado.ioloop.IOLoop.instance().start()
