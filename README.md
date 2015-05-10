# sohu_crawled
m.sohu.com爬虫

sohu.py为爬虫执行文件

crontab为定时模块的使用

<h3>执行方法</h3>
python sohu.py 
注意如果用定时模块启动默认是在后台运行。

<h3>思路</h3>

分3个步骤实现

1.递归检测域名的所有链接，并将错误链接记录。

2.性能优化。

3.多线程和定时功能的实现。

基本上前两条是在一起实现的，观察m.sohu.com页面源代码，多数是http开头的长链接以及/开头的短链接。将短链接补全并整合再次递归。递归要注意的是：非m.sohu.com域名下的页面只进行一级检测，及不再次进行链接页面的提取及检测，以免爬出外链。优化：除了过滤不必检测的链接和javascript之外，要注意链接的重复性，主页的多个频道一级回到主页等都只需检测一次即可。

<h3>疑问</h3>

检测时总会卡住不动，直接Python运行到500左右时可能会卡住，用Eclipse最检测到了7000+
优化：添加一个失败后自动重试的功能。

<h3>总结</h3>

这周都在学习爬虫，虽然还不是完全掌握了爬虫的个中知识，但是已经比一周前的小白状态有了更深入的了解，同时也暴露出自己的很多问题。Python和多线程方面还要加强。不会的东西还有很多，抓紧了。

<h3>下半个月：</h3>

看更深入一些的书《Python核心编程》《Python cook book》等。
多做一些Python的练习。
继续Django框架的学习以及MySQL的入门。
