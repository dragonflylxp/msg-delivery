#coding:utf-8
#File: db_tools.py
#Auth: lixp(@500wan.com)
#Date: 2014-09-23 16:41:33
#Desc: 


import redis

configs = {}
def set_up(confs):
    """设置默认（连接）参数
    """
    configs.update(confs)

redis_pools = {}
def get_redis(dbid, standalone=False):
    conf = configs['Redis'][dbid].copy()
    if standalone:
        conf.pop('max_connections', None)
        return redis.Redis(**conf)
    pool = redis_pools.get(dbid)
    if not pool:
        conf.setdefault('max_connections', 8)
        pool = redis.ConnectionPool(**conf)
        redis_pools[dbid] = pool
    return redis.Redis(connection_pool=pool)
