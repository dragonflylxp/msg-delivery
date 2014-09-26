#coding:utf-8
#File: timer_procedure.py
#Auth: lixp(@500wan.com)
#Date: 2014-09-22 15:40:45
#Desc: 

import tornado.ioloop
import tornado.httpclient
import os,sys,time
import functools
import threading,ujson,urllib
from Queue import Queue,PriorityQueue 

APP_PATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
sys.path.append(os.path.join(APP_PATH,'lib'))
import msg_procedure
import db_tools
from events import msgEvent 
from logger import Log

logger = Log().getLog()
#REDIS_TIMER_LST      = "msg_timer_list" 
#REDIS_EVT_LST_PREFIX = "msg_event_list_"
REDIS_TIMER_LST      = "test_timer"
REDIS_EVT_LST_PREFIX = "test_msg_"

class msgTimer(object):
    def __init__(self):

        """按时间排序,从小到大
        self.Q = myPriorityQueue()
        self.Q.change_lock()
        """
        self.Q = Queue()
        self.R = db_tools.get_redis("timer") 
        self.reload_evt()

    def save_evt(self, evt):
        key = REDIS_EVT_LST_PREFIX + evt.t
        val = ujson.dumps(evt, ensure_ascii=False)
        self.R.rpush(key, val)
        #设置redis事件list的超时时间
        delt = int(evt.t) - int(time.time()) + 60
        self.R.expire(key,delt)

    def remove_evt(self, t):
        key = REDIS_EVT_LST_PREFIX + t
        self.R.delete(key)

    def save_t(self, t):
        self.R.rpush(REDIS_TIMER_LST, t)

    def remove_t(self, t):
        self.R.lrem(REDIS_TIMER_LST, t)

    def exist_t(self, t):
        key = REDIS_EVT_LST_PREFIX + t
        return self.R.exists(key)

    def send(self, evt):
        self.Q.put(evt)

    """重启时,reload定时事件
    """
    def reload_evt(self):
        #遍历timer_lst
        len_t = self.R.llen(REDIS_TIMER_LST)
        logger.info("Reload %d timer(s) from %s!" % (len_t, REDIS_TIMER_LST))
        empty_t = []
        for i in range(len_t):
            t = self.R.rpoplpush(REDIS_TIMER_LST, REDIS_TIMER_LST)

            #遍历evt_lst
            key = REDIS_EVT_LST_PREFIX + t
            len_evt = self.R.llen(key)
            logger.info("Reload %d event(s) from %s!" % (len_evt, key))
            
            #标记已失效的t
            if len_evt == 0:
                empty_t.append(t)
                continue
            
            #创建t时刻事件回调
            try:
                callback = functools.partial(self.timeout_callback, t)
                tornado.ioloop.IOLoop.instance().add_timeout(int(t), callback)
            except Exception,e:
                logger.error("Tornado add timeout error! [ ERROR:%s ]" % e)
            logger.info("Set event-timer's callback![ TIME:%s ]" % t)

        #删除已失效的t
        for t in empty_t:
            self.remove_t(t)
            logger.info("Remove a expire or empty event-timer![ TIME:%s ]" % t)

    """
        定时事件存储方式:
        时间戳列表
        key_t_lst--> [t1, t2, ...]

        事件列表
        key_lst_t1 --->[evt1, evt2, evt3...]
        key_lst_t2 --->[evt4, evt5, evt6...]
        ...
    """
    def process(self, evt):
        if not self.exist_t(evt.t):
            #持久化时间戳
            self.save_t(evt.t)
            logger.info("Save a event-timer![ TIME:%s ]" % evt.t)

            #建立定时任务
            try:
                callback = functools.partial(self.timeout_callback, evt.t)
                tornado.ioloop.IOLoop.instance().add_timeout(int(evt.t), callback)
            except Exception,e:
                logger.error("Tornado add timeout error! [ ERROR:%s ]" % e)
            logger.info("Set event-timer's callback![ TIME:%s ]" % evt.t)

        #持久化事件(设置过期时间)
        self.save_evt(evt)
        logger.info("Save a event-list![ KEY:%s ]" % (REDIS_EVT_LST_PREFIX + evt.t))

    def timeout_callback(self, t):
        logger.debug("Event-timer callback![ TIMER:%s NOW:%s ]" % (t, time.time()))
        #将t时刻的事件全部处理
        key = REDIS_EVT_LST_PREFIX + t
        len = self.R.llen(key)
        logger.debug("Scan event list![ KEY:%s TOTAL:%d ]" % (key, len))
        for i in range(len):
            str = self.R.lpop(key)
            logger.debug("Pop a event from list![ KEY:%s EVT:%s ]" % (key, str))
            if not str: continue 
            dct = ujson.loads(str)
            evt = msgEvent().from_dict(dct)
            msg_procedure.process(evt)  

        #清除cache
        self.remove_evt(t)
        logger.info("Remove a event-list![ KEY:%s ]" % key)
        self.remove_t(t)
        logger.info("Remove a event-timer![ TIME:%s ]" % t)

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
