import requests
import re
import time
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
import asyncio
import aiohttp
import threading
import logging
import pickle

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - line:%(lineno)d - %(levelname)s - %(message)s"
)
ch = logging.StreamHandler()
fh = logging.FileHandler(f"auto_vote_{time.strftime('%Y%m%d')}.log")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)



mutex = threading.Lock()
# 定义全局变量


class BbsMonitor(object):

    def __init__(self, url, keywords=[]):
        self.url = url  # 网站的根地址
        self.keywords = keywords
        self.regex = re.compile("|".join(keywords))
        self.all_inner_urls = set()
        self.warn_urls = set()
        # 定义一个队列,供多线程共享使用.
        self.queue = set()

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
        }

    async def isWarningSite2(self, url):
        '''
        异步判断一个网站是否含有关键字
        '''
        # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as resp:
                html = await resp.text(errors = 'ignore')
                if re.findall(self.regex, html):
                    self.warn_urls.add(url)


    async def asyn_tasks_isWarn(self, urls):
        tasks = [asyncio.create_task(self.isWarningSite2(url)) for url in urls]
        await asyncio.gather(*tasks,return_exceptions=True)



    def isWarningSite(self, url):
        '''
        判断一个网站是否含有关键词
        '''
        try:
            r = requests.get(url, headers=self.headers)
            if re.findall(self.regex, r.text):
                mutex.acquire()
                self.warn_urls.add(url)
                mutex.release()
                return True
            return False
        except:
            pass
        return False

    async def get_innner_links2(self, link):
        '''
        获取单个网站所有内部链接，返回集合元素，自动去重
        '''
        inner_links = set()
        async with aiohttp.ClientSession() as session:
            async with session.get(link, timeout=30) as resp:
                html = await resp.text(errors = 'ignore')
                soup = BeautifulSoup(html, "html.parser")
                for link in soup.find_all('a', href=re.compile("^(thread|forum|http.*://bbs.wjdaily.com/)")):
                    if "href" in link.attrs:
                        href = link.attrs['href']
                        if not href.startswith('http'):
                            href = self.url+href
                        inner_links.add(href)
            return inner_links

    async def asyn_tasks_getInnerLinks(self, urls):
        tasks = [asyncio.create_task(self.get_innner_links2(url)) for url in urls]
        res = await asyncio.gather(*tasks,return_exceptions=True)
        self.queue = self.queue.union(*[r for r in res if isinstance(r,set)])
        self.queue =self.queue.difference(self.all_inner_urls) #self.queue - self.all_inner_urls

    def get_all_innner_links(self):
        '''
        采用广度优先搜索算法，获取网站所有内部链接
        '''
        # links = self.get_innner_links(self.url)

        asyncio.run(self.asyn_tasks_getInnerLinks([self.url]))
        self.all_inner_urls = self.all_inner_urls.union(self.queue)
        for k in range(2):            
            links = self.queue.copy()
            self.queue.clear()
            links = list(links)
            num = len(links)            
            logger.info(f"{time.strftime('%T')}：{num}")
            i = 0 
            while i < num:
                begin = i
                end = i+500
                if end>num:
                    end = num
                i += 500
                logger.info(f"{time.strftime('%T')}：{begin,end}")
                asyncio.run(self.asyn_tasks_getInnerLinks(links[begin:end]))
                self.all_inner_urls = self.all_inner_urls.union(self.queue)

    def save_inner_links_of_single_site(self, url):
        self.all_inner_urls = self.all_inner_urls.union(
            self.get_innner_links(url))


# keywords = [
#     "揭发一个低素质政府工作人员",
#     "恶心的反胃",
# ]

# for link in soup.find_all("a"):
#    if link.get("href") and link.get("href").startswith("thread"):
#        inner_urls.append(url + link.get("href"))
# return inner_urls

if __name__ == "__main__":
    keywords = ['lilili','你好']
    begin = time.time()
    bbs = BbsMonitor('https://bbs.wjdaily.com/bbs/', keywords=keywords)
    # bbs.get_all_innner_links()
    # pickle.dump(bbs.all_inner_urls,file=open("data.pickle","wb"))

    all_inner_urls = pickle.load(file= open("data.pickle","rb"))
    bbs_num = len(all_inner_urls)
    logger.info(f"获取不同的内部链接{bbs_num}个")
    print(len(all_inner_urls))
    #print(bbs.all_inner_urls)
    # begin = time.time()
    # bbs = BbsMonitor('https://bbs.wjdaily.com/bbs/')
    # links1 = bbs.get_innner_links(bbs.url)
    # print(len(links1))
    # bbs.all_inner_urls = bbs.all_inner_urls.union(links1)
    #with ThreadPool(processes=10) as executor:
    #    executor.map(bbs.isWarningSite, bbs.all_inner_urls)
    #print(bbs.warn_urls)
    i = 0
    all_inner_urls_list = list(all_inner_urls)
    # asyncio.run(bbs.asyn_tasks_isWarn(all_inner_urls_list))
    while i < bbs_num:
        begin = i
        end = i + 500
        if end > bbs_num:
            end = bbs_num
        i += 500
        logger.info(f"{begin} - {end}")
        asyncio.run(bbs.asyn_tasks_isWarn(all_inner_urls_list[begin:end]))
        logger.info(bbs.warn_urls)
    end = time.time()
    logger.info(f"耗时 {end-begin} 秒")

    # # 发送邮件
    message = {
        'subject': "东太湖论坛舆情监控",
        'message': f"在{bbs_num}个帖子中找到含有关键字{keywords}的网站有:\n{bbs.warn_urls}\n耗时{end-begin}秒",
        'from_email': 'somenzz@163.com',
        'to_email': 'somenzz@163.com'
    }
    logger.info(message)
