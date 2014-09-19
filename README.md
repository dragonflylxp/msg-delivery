msg-delivery
============

消息分发系统(支持实时消息、定时消息发送，支持单条消息和批量消息)

1.基于tornado的web服务
2.Timer管理器，rb_tree_queue维护消息事件
3.持久化消息事件防止宕机
