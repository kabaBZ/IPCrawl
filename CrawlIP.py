from IPCrawl import IPCrawl
import requests
import random
import time
import json
from lxml import etree
from redis import Redis
from bs4 import BeautifulSoup
import copy
import sched
import schedule
# def timer():
#     #初始化模块
#     scheduler = sched.scheduler(time.time,time.sleep)
#     #增加任务，enter（睡眠时间，执行级别，执行函数）
#     scheduler.enter(5, 1, action)
#     #运行任务
#     scheduler.run()
def timer():
    schedule.every().day.at("05:00").do(crawl)
    while True:
        schedule.run_pending()
        time.sleep(3600)

def crawl():
    a = IPCrawl.KuaidailiProxy()
    b = IPCrawl.FatezeroIP()
    c = IPCrawl.JiangxianliIP()
    d = IPCrawl.Ip3366()
    e = IPCrawl.YqieProxy()
    f = IPCrawl.ZdayeProxy()
    g = IPCrawl.TaiyangProxy()
    h = IPCrawl.Ip66Proxy()
    i = IPCrawl.SeofangfaProxy()
    print('kuaidaili')
    a.proxy_to_redis()
    print('fatezero')
    b.proxy_to_redis()
    print('jiangxianli')
    c.proxy_to_redis()
    print('ip3366')
    d.proxy_to_redis()
    print('yqie')
    e.proxy_to_redis()
    print('taiyang')
    # f.proxy_to_redis()
    g.proxy_to_redis()
    print('ip66')
    h.proxy_to_redis()
    print('seofangfa')
    i.proxy_to_redis()
crawl()