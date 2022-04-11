import copy
import random
import requests
import time
from lxml import etree
from redis import Redis
import random
from copy import deepcopy

# 爬取代理的URL地址，选择的是快代理
url_ip ="https://www.kuaidaili.com/free/inha/"
# 设定等待时间
set_timeout =5
# 爬取代理的页数，2表示爬取2页的ip地址
# num =5
# 代理的使用次数
count_time =5
# 构造headers
headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}
# 测试ip的URL
url_for_test ='http://httpbin.org/ip'
conn = Redis(host='localhost',port=6379)
proxies ={
        'http': '150.109.32.166:80',  #'http://'+
        }
#本次更新条数
def scrawl_kuai_ip(num):
    '''
    爬取代理ip地址
    '''
    ip_list =[]
    for num_page in range(1,num+1):
        url = url_ip + str(num_page)
        response = requests.get(url,headers=headers,) #,proxies = proxies需要时可设置代理
        print(response)
        if response.status_code ==200:
            content = response.text
            tree = etree.HTML(content)
            tr_list = tree.xpath('/html/body/div[1]/div[4]/div[2]/div[2]/div[2]/table/tbody/tr')
            for tr in tr_list:
                ipv4 = tr.xpath('./td[1]/text()')[0]
                port = tr.xpath('./td[2]/text()')[0]
                ip = ipv4 + ':' + port
                ip_list.append(copy.deepcopy(ip))
        print(ip_list)
        #不睡封ip
        time.sleep(5)
    ip_set = set(ip_list)  # 去掉可能重复的ip
    ip_list = list(ip_set)
    print(ip_list)
    return ip_list
def ip_test(url_for_test,ip_info):
    '''
    测试爬取到的ip，测试成功则存入Redis
    '''
    n = 0
    for ip_for_test in ip_info:
        # 设置代理
        proxies ={
        'http': ip_for_test,  #'http://'+
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
    将测试通过的ip存入Redis
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
    useful_proxy_list_bytes = list(conn.smembers('Proxies'))
    useful_proxy_list = []
    for bytes in useful_proxy_list_bytes:
        bytes = bytes.decode('utf-8')
        useful_proxy_list.append(bytes)
    print(useful_proxy_list)
    useful_proxy = random.choice(useful_proxy_list)
    proxy ={
    'http' : str(useful_proxy),
    }
    try:
        response = requests.get(url_for_test,headers=headers,proxies=proxy,timeout=5)
        if response.status_code ==200:
            print('此ip未失效:',useful_proxy)
            return useful_proxy
    except Exception as e:
        print('此ip已失效:',useful_proxy)
        conn.srem('Proxies',useful_proxy)
        print('已经从Redis移除')
        get_random_ip()
def main():
    #爬取代理ip5页
    ip_info = scrawl_kuai_ip(5)
    #测试ip是否可用并存储至redis
    ip_test(url_for_test,ip_info)
    #随机取ip
    finally_ip = get_random_ip()
    print('取出的ip为：',finally_ip)
if __name__ =='__main__':
    main()