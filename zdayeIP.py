import copy
import time
from redis import Redis
import requests
from lxml import etree
import random
from copy import deepcopy

main_url = 'https://www.zdaye.com/dayProxy/1.html'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
}
ip_list = []
url_for_test ='http://httpbin.org/ip'
#第二页ipURL
ip2_url_list = []
url_list = []
conn = Redis(host='localhost',port=6379)
proxies ={
        'http': '47.108.234.147:8088',  #'http://'+
        }
def get_detail_url(url):
    x = 0
    detail_url_list = []
    main_data = requests.get(url,headers = headers,proxies = proxies)
    main_data.encoding = 'gbk'
    tree = etree.HTML(main_data.text)
    detail_url_xpath = tree.xpath('//div[@class = "thread_item"]//h3/a/@href')
    for xpath in detail_url_xpath:
        x += 1
        detail_url_list.append(copy.deepcopy('https://www.zdaye.com' + xpath))
        url_list.append(copy.deepcopy('https://www.zdaye.com' + xpath))
        if x == 4 :
            break
    return detail_url_list
def parse_detail_url(url):
    detail_url_2 = url.split('.html')[0]+'/2'+'.html'
    url_list.append(copy.deepcopy(detail_url_2))
def parse_ip(url):
    data = requests.get(url ,headers = headers,proxies = proxies)
    data.encoding = 'gbk'
    print(data.text)
    tree = etree.HTML(data.text)
    tr_list = tree.xpath('/html/body/div[3]/div/div[2]/div/div[5]/table//tr')
    for tr in tr_list:
        ipv4 = tr.xpath('./td[1]/text()')[0]
        port = tr.xpath('./td[2]/text()')[0]
        ip = ipv4 + ':' + port
        ip_list.append(copy.deepcopy(ip))
        print(ip)
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
                print('测试通过:',proxies)
                x = write_to_Redis(ip_for_test)
                if x == 1:
                    n += 1
        except Exception as e:
            print('测试失败:',proxies)
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
    get_random_ip()
    for url in get_detail_url(main_url):
        parse_detail_url(url)
    # for url in url_list:
    #     parse_ip(url)
    #     time.sleep(5)
    parse_ip(url_list[0])
    print(ip_list)
    ip_test(url_for_test,ip_list)
if __name__ =='__main__':
    main()
