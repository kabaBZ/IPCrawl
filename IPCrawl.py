import copy
import random
import requests
import time
from lxml import etree
from redis import Redis
from copy import deepcopy
# 爬取代理的URL地址，选择的是西刺代理
url_ip ="https://www.kuaidaili.com/free/inha/"
# 设定等待时间
set_timeout =5
# 爬取代理的页数，2表示爬取2页的ip地址
num =1
# 代理的使用次数
count_time =5
# 构造headers
headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}
# 测试ip的URL
url_for_test ='http://httpbin.org/ip'
conn = Redis(host='localhost',port=6379)
#本次更新条数
def scrawl_kuai_ip(num):
    '''
    爬取代理ip地址
    '''
    ip_list =[]
    ip = {}
    for num_page in range(1,num):
        url = url_ip + str(num_page)
        response = requests.get(url,headers=headers)
        if response.status_code ==200:
            content = response.text
            tree = etree.HTML(content)
            tr_list = tree.xpath('/html/body/div[1]/div[4]/div[2]/div[2]/div[2]/table/tbody/tr')
            for tr in tr_list:
                ipv4 = tr.xpath('./td[1]/text()')[0]
                port = tr.xpath('./td[2]/text()')[0]
                ip = ipv4 + ':' + port
                ip_list.append(copy.deepcopy(ip))
                ip_set = set(ip_list)  # 去掉可能重复的ip
                ip_list = list(ip_set)
    print(ip_list)
    return ip_list
def ip_test(url_for_test,ip_info):
    '''
    测试爬取到的ip，测试成功则存入MongoDB
    '''
    n = 0
    for ip_for_test in ip_info:
        # 设置代理
        proxies ={
        'http': ip_for_test,  #'http://'+
        # 'https':'http://'+ ip_for_test['ip']+':' + ip_for_test['port'],
        }
        try:
            response = requests.get(url_for_test,headers=headers,proxies=proxies,timeout=5)
            if response.status_code ==200:
                print('测试通过:')
                print(proxies)
                x = write_to_Redis(ip_for_test)
                if x == 1:
                    n += 1
        except Exception as e:
            print('测试失败：')
            print(proxies)
            continue
    print('本次向数据库更新数目:',n)
def write_to_Redis(proxies):
    '''
    将测试通过的ip存入MongoDB
    '''
    ex = conn.sadd('Proxies',proxies)
    if ex == 1:
        print('Proxies更新成功')
        return 1
    else:
        print('已存在，未更新。')
        return 0
def get_random_ip():
    '''
    随机取出一个ip
    '''
    client = pymongo.MongoClient(host='localhost',port=27017)
    db = client.PROXY
    collection = db.proxies
    items = collection.find()
    length = items.count()
    ind = random.randint(0,length-1)
    useful_proxy = items[ind]['ip'].replace('\n','')
    proxy ={
    'http':'http://'+ useful_proxy,
    'https':'http://'+ useful_proxy,
    }
    response = requests.get(url_for_test,headers=headers,proxies=proxy,timeout=10)
    if response.status_code ==200:
        return useful_proxy
    else:
        print('此{ip}已失效'.format(useful_proxy))
        collection.remove(useful_proxy)
        print('已经从MongoDB移除')
        get_random_ip()
def main():
    ip_info =[]
    ip_info = scrawl_kuai_ip(2)
    ip_test(url_for_test,ip_info)
    # finally_ip = get_random_ip()
    # print('取出的ip为：'+ finally_ip)
if __name__ =='__main__':
    main()