import tornado.web,tornado.ioloop,tornado.httpserver
from tornado.options import define,options
from tornado.websocket import WebSocketHandler as Basewebsocket
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from threading import Thread
import json
import pytz

def get_scheduler():
    """创建定时任务对象"""
    executors = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }
    scheduler = BlockingScheduler(executors=executors, job_defaults=job_defaults,
                                  timezone=pytz.timezone('Asia/Shanghai'))
    return scheduler


class WebSocketHandler(Basewebsocket):
    socket_users = dict()  # 用来存放在线用户的容器

    @classmethod
    def route_urls(cls):
        return [(r'/', cls, {}), ]

    @staticmethod
    def send_messages():
        """向所有连接的客户端发送消息"""
        if len(WebSocketHandler.socket_users)>0:
            dic = {"data":"服务器主动向客户端推送信息"}
            for socket_user in WebSocketHandler.socket_users.values():
                socket_user.write_message(json.dumps(dic).encode("utf-8"))
                print("发送消息成功")
        else:
            print("没有客户端链接")

    @staticmethod
    def send_message(message, target):
        """向指定用户发送消息"""
        date = {"text":message}
        socket_user = WebSocketHandler.socket_users.get(target)
        socket_user.write_message(json.dumps(date).encode("utf-8"))
        print("send_message")

    def open(self):
        self.socket_users[str(id(self))] = self  # 建立连接后添加用户到容器中
        print(self.socket_users)

    def on_message(self, message):
        mes = json.loads(message)   #对接收到的参数进行处理
        target = mes["name"]
        text =  mes["text"]
        WebSocketHandler.send_message(text,target)  #向指定用户发送消息

    def on_close(self):
        self.socket_users.pop(str(id(self)), None)  # 用户关闭连接后从容器中移除用户
        print("on_close")

    def check_origin(self, origin):
        return True  # 允许WebSocket的跨域请求



def initiate_server():
    define('port', default=4041, help='port to listen on')
    app = tornado.web.Application(WebSocketHandler.route_urls())    # 创建tornado应用程序并提供url
    server = tornado.httpserver.HTTPServer(app) # 设置服务器
    server.listen(options.port) #设置监听端口
    tornado.ioloop.IOLoop.instance().start()    # 开始io /event 循环


def add_job():
    scheduler = get_scheduler()   #获取scheduler对象
    #添加定时任务每30秒执行一次
    scheduler.add_job(WebSocketHandler.send_messages, 'interval', seconds=30, max_instances=1)
    scheduler.start()   #启动定时任务


if __name__ == '__main__':
    t1 = Thread(target=initiate_server)
    t2 = Thread(target=add_job)
    t1.start()
    t2.start()

