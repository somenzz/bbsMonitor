# bbsMonitor
利用百度对论坛的一些关键词进行监控，并将查询结果截图发送邮件。

至于为什么使用百度，是因为自己写的多线程，协程并发去搜索网页内容还是太慢，查 13 万网页近 2 个小时，还不如百度呢，30 分钟前发过的帖子，使用百度就能搜索到。

使用之前需要安装依赖库：

```python
pip install splinter
pip install smtplib
pip install bs4 
```

使用方法：

1、修改settings.py 文件，填写为自己的邮箱信息，接收邮件信息。

2、定时任务调起以下任务：
```python
python see_wjdaily_from_baidu.py
```

说明：如果不想使用百度，想自己写并发程序查询，可参考文件 wjdaily3.py。 个人感觉还是搜索引擎好用，人家才是专业的爬虫。