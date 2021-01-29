from websocket import create_connection
from threading import Thread
import json

"""
模拟浏览器websocket进行通信
"""

def message(name,text):
    return {
        "name":name,
        "text":text
    }

def short_lived_connection(ws):
    while True:
        print("请输入收件人及发送的内容：")
        name = input()
        text = input()
        if name == "E":
            ws.close()  #关闭连接
        resul = json.dumps(message(name,text))  #构造发送的数据及接收的用户
        ws.send(resul)  #向服务端发送数据

def recvs(ws):
    while True:
        result = ws.recv()  #接收数据
        print("Received '%s'" % json.loads(result))

if __name__ == '__main__':
    ws = create_connection("ws://localhost:4041/")
    threads = [
        Thread(target=short_lived_connection, args=(ws,)),
        Thread(target=recvs, args=(ws,))
    ]
    for i in threads:
        i.start()
    for r in threads:
        r.join()