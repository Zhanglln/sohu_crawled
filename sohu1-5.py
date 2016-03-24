#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
1.定时递归检测所有m.sohu.com域名的页面以及这些页面上的链接的可达性，即有没有出现不可访问情况。
2.m.sohu.com域名页面很多，从各个方面考虑性能优化。
3.对于错误的链接记录到日志中，日志包括：连接，时间，错误状态等。
4.考虑多线程的方式实现。
'''
import os
import time
import logging
import urllib2
from Queue import Queue
from urlparse import urlparse, urljoin
from bs4 import BeautifulSoup
from threading import Thread

# 定义线程的数量
threads_num = 5

# 开始域名,这里最后不能加 / 因为要添加短链接，短链接前面已经有一个 /
starturl = 'http://m.sohu.com'

#队列
qu = Queue()

# 初始化log
logging.basicConfig(filename = os.path.join(os.getcwd(), time.strftime('%Y-%m-%d-') + 'log.txt'),
        level = logging.WARN, filemode = 'a', format = '错误时间：%(asctime)s  %(message)s')

# 不进行检测的url，None表示如果有为空的href则跳过，电脑版不检测
not_checked = ['/', None, 'http://m.sohu.com/towww', 'javascript:;','javascript:void(0);','javascript:window.scrollTo(0,0);']
# 线程类
class MyThread(Thread):

    def __init__(self, func):
        super(MyThread, self).__init__() #调用父类的构造函数
        self.func = func #传入线程函数逻辑
	
    def run(self):
		self.func()

def worker():
	while qu.empty() == False:
		url = qu.get()  
		check_page_links(url)
		time.sleep(1)
		qu.task_done()

def check_page_links(url):   
    print '\n进入页面： %s\n' % url
    # 提取页面链接
    links = get_all_links(url)
    num = len(links)
    for link in links:
        href = link.get('href')
        num -= 1
        # 如果没检测过则加入列表下次不再检测
        if href not in not_checked:
            not_checked.append(href)
            #短链接前加上 m.sohu.com                 
            url = get_whole_url(href)
            print '第%d个url' % (int(len(not_checked)) - 6)
            get_url_msg(url)  
        #当数组中最后一个元素在not_checked中时     
        if num == 0:
            break
        else:
             continue
        
# 读取页面链接
def get_all_links(url):
    text = urllib2.urlopen(url).read()
    soup = BeautifulSoup(text)
    return soup.find_all('a')

def get_whole_url(url):
		uhost = urlparse(url)
		if uhost.netloc == '':
			url = urljoin('http://m.sohu.com',url)
			return url.encode('utf-8')
		else:
			return url.encode('utf-8')

# 检查链接的有效性并将错误信息写到日志
def get_url_msg(url):
    headers = {
'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36' ,
'Referer':'http://m.sohu.com'
}
    req = urllib2.Request(url, headers = headers)
    print '\nURL: %s\n' % url

    try:
        code = urllib2.urlopen(req, timeout=5).getcode()
        tiaozhuan = urllib2.urlopen(req, timeout=5).geturl()
        uhost = urlparse(tiaozhuan)
        if code in [200, 302]:
            if uhost.netloc.find('sohu.com') != -1:
                qu.put(tiaozhuan)
                print '访问成功' 
                print '\n' + '-' * 50 + '\n'                        
            else:
                print '访问成功,但重定向为外链，不加入队列'
                print '\n' + '-' * 50 + '\n'
                return
        else:
            print 'Error Code: %s' % code
            print '\n' + '#' * 50 + '\n'
            write_log('warning', url, code )
            
    except Exception, e:
        print str(e) 
        print '\n' + '*' * 50 + '\n'
        write_log('error', url, str(e))
    # 防止短时间内链接过于频繁
    time.sleep(1)

# 写入日志
def write_log(log_type, url, message):
    logger = '\n错误链接：%s\n错误信息：%s\n%s\n' % (url, message, '-'*50)
    if log_type == 'error':
        logging.error(logger)
    elif log_type == 'warning':
        logging.warning(logger)

def main():
    threads = []
    qu.put(starturl) # 加入队列

    for i in range(threads_num):
		t = MyThread(worker)
		t.start()
		threads.append(t)

    for t in threads:
		t.join()
    qu.join()
    print "-----Spider Successful!!!------"

if __name__ == '__main__':
    main()


