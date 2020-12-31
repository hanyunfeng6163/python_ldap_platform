# -*- coding: utf-8 -*
# @author: 韩云峰
# @time: 2019/3/21 16:14

import redis
from django.conf import settings


class cacheRedis:
    def __init__(self):
        self.con = redis.Redis(host=settings._REDIS_HOST, port=settings._REDIS_PORT, decode_responses=True)

    def setTicket(self, timeout, **kwargs):
        ticket = str(kwargs.get("ticket"))
        self.con.hmset(ticket, kwargs)
        self.con.expire(name=ticket, time=timeout)
        # return self.con.set(ticket,str(kwargs),ex=timeout)

    def findTicket(self, ticket):
        return self.con.hgetall(ticket)

    def delTicket(self, ticket):
        return self.con.delete(ticket)


if __name__ == '__main__':
    redis_conn = cacheRedis()
    # data={'username': u'root', 'ticket': '8d3f178b96f9331aa0851682b771f06d-a23b9754-4804-3f05-8322-2fce3022973a', 'domain': u'192.168.1.157:8000', 'time': 1553072772.362519}
    # redis_conn.setTicket(50,**data)
    # print(redis_conn.findTicket('4c93adf3-cf19-3bbc-a294-2fd45ace787c'))
