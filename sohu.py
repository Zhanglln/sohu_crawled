#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import logging
import urllib2

from Queue import Queue
from httplib import HTTP
from random import choice
from bs4 import BeautifulSoup
from threading import Thread, RLock
from urlparse import urlparse, urljoin

# 已访问的网址,避免重复
visited = []

# 已检测的网址
checked = []
checked_num = 0

# 定义线程的数量
WORKS_NUM = 5

# 域名,这里最后不能加 / 因为要添加短链接，短链接前面已经有一个 /
DOMAIN = 'http://m.sohu.com'

# 线程锁
mylock = RLock()

# 初始化log
logging.basicConfig(filename = os.path.join(os.getcwd(), time.strftime('%Y-%m-%d-') + 'log.txt'),
        level = logging.WARN, filemode = 'a', format = '错误时间：%(asctime)s  %(message)s')

# 不进行检测的url，包括：普版、彩版、触版、PC.
not_check = [None, '#', '/', '#top' 
            '?v=2&_once_=sohu_version_2', 
            'http://m.sohu.com/towww', 
            'http://m.sohu.com/towww?_smuid=Fp2BA2eH7zvswZMa9vrD2U&amp;v=2',
            '?v=1&amp;_once_=sohu_version_1&amp;_smuid=Fp2BA2eH7zvswZMa9vrD2U', 
            '?v=3&amp;_once_=sohu_version_3&amp;_smuid=Fp2BA2eH7zvswZMa9vrD2U',
            '?v=3&amp;_once_=000025_v2tov3&amp;_smuid=Fp2BA2eH7zvswZMa9vrD2U',
        ]

# 线程类
class CheckThread(Thread):
    def __init__(self, qe, no):
        Thread.__init__(self)
        self._qe = qe # 队列
        self._no = no # 第几线程
        self.threads = 0 # 判断线程的数量

    def run(self):
        # 每运行一个线程线程+1
        self.threads += 1

        while True:
            if self._qe.qsize() > 0: # 如果列队中还有Url则继续线程继续执行
                self._work(self._qe.get(), self._no)
            else:
                # 当线程关闭-1
                self.threads -= 1
                # 如果线程都结束则关闭日志文件
                if self.threads == 0:
                    logging.shutdown()
                break

    def _work(self, url, no):
        check_page_links(url, no)


def check_page_links(url, no):
    global checked_num
    print '第%d个进程：' % no
    print '进入页面： %s' % url
    # 提取页面链接
    links = get_all_links(url)

    for link in links:
        href = link.get('href')

        # 过滤不需要检测的URL以及javascript
        if href in not_check:
            continue
        elif href.find('javascript', 0, 10) != -1:
            continue
         # 获得完整的url
        whole_url = get_whole_url(href)
        if whole_url in checked:
            continue

        mylock.acquire()
        checked.append(whole_url)
        checked_num += 1
        # 防止短时间内链接过于频繁
        if checked_num % 2000 == 0:
            time.sleep(5)
        mylock.release()

        print '第%s个url' % checked_num

        # 检查链接是否可达
        get_url_msg(whole_url)

        # 只要 m.sohu.com 域名下的链接
        if whole_url.find('http://m.sohu.com/', 0, 19) == 0:
            # 去重
            if whole_url not in visited:
                try:
                    check_page_links(whole_url, no)
                except Exception, e:
                    write_log('error', whole_url , str(e) )


# 读取页面链接
def get_all_links(url):
    text = urllib2.urlopen(url).read()
    soup = BeautifulSoup(text)
    return soup.find_all('a')


# 获得完整的url，把短链接前加上 http://m.sohu.com
def get_whole_url(url):
    uhost = urlparse(url)
    
    if uhost.netloc == "":
        url = urljoin(DOMAIN, url)

    return url.encode('utf-8')


# 检查链接的有效性并将错误信息写到日志
def get_url_msg(url):
#    start_time = time.time()
    headers = {
'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36' ,
'Referer':'http://m.sohu.com'
}
    req = urllib2.Request(url , headers = headers)

    print '\nURL: %s\n' % url

    try:
        # 检查网址的开始时间
#        utime = time.time()
        code = urllib2.urlopen(req, timeout=5).getcode()
        if code in [200, 302]:
            print '访问成功'
            print '\n' + '-' * 50 + '\n'
        else:
            print 'Error Code: %s' % code
            print '\n' + '#' * 50 + '\n'
            # 写入日志
            write_log('warning', url , code )
    except Exception, e:
        print str(e)
        print '\n' + '*' * 50 + '\n'
        # 写入日志
        write_log('error', url , str(e))

    # 防止短时间内链接过于频繁
    time.sleep(1)



# 写入日志
def write_log(log_type, url , message):
    logger = '\n错误链接：%s\n错误信息：%s\n%s\n' % (url, message, '-'*50)
    if log_type == 'error':
        logging.error(logger)
    elif log_type == 'warning':
        logging.warning(logger)


if __name__ == '__main__':
    # 页面入口 m.sohu.com 导航页面
    WEBSITE = 'http://m.sohu.com/c/395/?_once_=000025_top_daohang_v2&_smuid=B3c57lC0yV68YNhqcs02Ul&v=2'
    # 提取导航页面
    nav_text = urllib2.urlopen(WEBSITE).read().decode('utf-8')
    # 页面soup，所有标签
    nav_soup = BeautifulSoup(nav_text)
    # 获得需要检查的栏目,以 bd2 开头
    bd2 = nav_soup.find_all('p', 'bd2')
    # 创建队列
    q = Queue(0)
    for column in bd2:
        if column.a:
            nav_url = DOMAIN + column.a.get('href')
            q.put(nav_url) # 加入队列
            checked.append(nav_url)

    for i in range(0, WORKS_NUM):
        CheckThread(q, i + 1).start()

