import requests


# 构造headers
headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}
# 测试ip的URL
url_for_test ='http://httpbin.org/ip'
url_ip ="https://www.kuaidaili.com/free/inha/2"
proxy = proxies ={
        'http': '150.109.32.166:80',  #'http://'+
        }
for num_page in range(1,5):
    print(num_page)
try:
    response = requests.get(url_ip, headers=headers, proxies=proxy, timeout=5)
    if response.status_code == 200:
        print('此ip未失效:',proxy)
except Exception as e:
    print('此ip已失效:', proxy)
    print('已经从Redis移除')