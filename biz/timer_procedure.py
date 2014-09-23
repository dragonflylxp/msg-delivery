#coding:utf-8
#File: timer_procedure.py
#Auth: lixp(@500wan.com)
#Date: 2014-09-22 15:40:45
#Desc: 

import tornado.ioloop
import tornado.httpclient
import os,sys,time
import threading,ujson,urllib
from Queue import Queue,PriorityQueue 

APP_PATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
sys.path.append(os.path.join(APP_PATH,'lib'))
import db_tools

REDIS_TIMER_LST      = "EVT_TIMER_LST"
REDIS_EVT_LST_PREFIX = "EVT_LST_"

class msgTimer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        """按时间排序,从小到大
        self.Q = myPriorityQueue()
        self.Q.change_lock()
        """
        self.Q = Queue()
        self.R = db_tools.get_redis("timer") 
        self.reload_evt()

    def save_evt(self, evt):
        key = REDIS_EVT_LST_PREFIX + "%d" % evt.t
        val = ujson.dumps(evt, ensure_ascii=False)
        self.R.rpush(key, val)

    def remove_evt(self, evt):
        key = REDIS_EVT_LST_PREFIX + "%d" % evt.t
        self.R.del(key)

    def save_t(self, t):
        self.R.rpush(REDIS_TIMER_LST, evt.t)

    def remove_t(self, t):
        self.R.lrem(REDIS_TIMER_LST, 0, evt.t)

    def exist_t(self.t):
        key = REDIS_EVT_LST_PREFIX + "%d" % evt.t
        return self.R.exists(key)

    def send(self, evt):
        self.Q.put(evt)


    """重启时,reload定时事件
    """
    def reload_evt(self):
        #遍历timer_lst
        len_t = self.R.llen(REDIS_TIMER_LST)
        for i in range(len_t):
            t = self.R.rpoplpush(REDIS_TIMER_LST)
            
            #遍历evt_lst
            key = REDIS_EVT_LST_PREFIX + "%d" % evt.t
            len_evt = self.R.llen(key)
            for j in range(len_evt):
                evt = self.R.rpoplpush(key)
                tornado.ioloop.IOLoop.instance().add_callback(self.timeout_callback, evt)


    """定时事件存储方式:
        时间戳列表
        key_t_lst--> [t1, t2, ...]

        事件列表
        key_t1_lst --->[evt1, evt2, evt3...]
        key_t2_lst --->[evt4, evt5, evt6...]
        ...

    """
    def run(self):
        while True:
            #取出队首事件
            evt = self.Q.get()
            if evt is None:
                continue

            #持久化事件
            self.save_evt(evt)

            #持久化时间戳
            if not self.exist_t(evt.t):
                self.save_t(evt.t)

            #建立定时任务
            tornado.ioloop.IOLoop.instance().add_callback(self.timeout_callback, evt)

    def timeout_callback(self, evt):
        tornado.ioloop.IOLoop.instance().add_timeout(evt.t, self.post_callback, evt)

    def post_callback(self, evt):
        client  = tornado.httpclient.AsyncHTTPClient()
        params  = urllib.urlencode({'t':evt.t, 'u':evt.u, 'b':evt.b})
        request = tornado.httpclient.HTTPRequest('127.0.0.1:8776/',
                                                  method  = "POST",
                                                  headers = {'Content-Type':"application/x-www-form-urlencoded"},
                                                  body    = params) 
        client.fetch(request, self.request_callback)

    def request_callback(self):
        self.remove_evt(evt)
        self.remove_t(evt.t)
                    

class myPriorityQueue(PriorityQueue):
    """将Queue的Lock改为可重入的RLock
       方便更大粒度自定义加锁,保证可靠性
       ref:https://hg.python.org/cpython/file/2.7/Lib/Queue.py
    """
    def change_lock(self):
        self.mutex          = threading.RLock()
        self.not_empty      = threading.Condition(self.mutex)
        self.not_full       = threading.Condition(self.mutex)
        self.all_tasks_done = threading.Condition(self.mutex)
