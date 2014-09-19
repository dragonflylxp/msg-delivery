#coding:utf-8
#File: main.py
#Auth: lixp(@500wan.com)
#Date: 2014-09-19 17:13:40
#Desc: 


import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello world")
        
application = tornado.web.Application([(r"/",MainHandler),])

if __name__ == "__main__":
    application.listen(8776)
    tornado.ioloop.IOLoop.instance().start()
    
