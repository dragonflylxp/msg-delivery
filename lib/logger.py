# coding: utf-8

import logging.config
import logging
import time

class Log():
    logger = None

    @classmethod
    def set_up(cls, logfile, logger):
        logging.config.fileConfig(logfile)
        Log.logger = logging.getLogger(logger)

    def getLog(self):
        if Log.logger == None:
            Log.logger = logging.getLogger('simple')
        return Log.logger

    def log_it(func):
        def deco_func(*args, **kwargs):
            tt = time.time()
            ret = func(*args, **kwargs)
            logger.info('call_function: [%s] %s %s %s %s', func.__name__, args, kwargs, ret, time.time() - tt)
            return ret
        return deco_func
