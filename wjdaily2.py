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
        self.queue = []

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


    async def asyn_tasks(self, urls):
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
            async with session.get(url, timeout=30) as resp:
                html = await resp.text(errors = 'ignore')
                soup = BeautifulSoup(html, "html.parser")
                for link in soup.find_all('a', href=re.compile("^(thread|forum|http.*://bbs.wjdaily.com/)")):
                    if "href" in link.attrs:
                        href = link.attrs['href']
                        if not href.startswith('http'):
                            href = self.url+href
                        inner_links.add(href)
            # mutex.acquire()
            # self.queue.extend(inner_links.difference(self.all_inner_urls))
            # mutex.release()
            return inner_links


    # def get_innner_links(self, link):
    #     '''
    #     获取单个网站所有内部链接，返回集合元素，自动去重
    #     '''
    #     inner_links = set()
    #     try:
    #         r = requests.get(link, headers=self.headers, timeout=30)
    #         soup = BeautifulSoup(r.text, "html.parser")
    #         for link in soup.find_all('a', href=re.compile("^(thread|forum|http.*://bbs.wjdaily.com/)")):
    #             if "href" in link.attrs:
    #                 href = link.attrs['href']
    #                 if not href.startswith('http'):
    #                     href = self.url+href
    #                 inner_links.add(href)
    #         mutex.acquire()
    #         self.queue.extend(inner_links.difference(self.all_inner_urls))
    #         mutex.release()
    #         return inner_links
    #     except Exception as e:
    #         print(f"{link} - {e}")
    #         pass
    #     return {}

    def get_all_innner_links(self):
        '''
        采用广度优先搜索算法，获取网站所有内部链接
        '''
        queue = []
        links = self.get_innner_links(self.url)
        # 先在队列中填充首页的内部链接,作为根链接.
        self.queue.extend(links)
        num = 1
        while self.queue != []:
            unvisied_links = [link for link in self.queue if link not in self.all_inner_urls]
            logger.info(f"第 {num} 层遍历, 获取 {len(unvisied_links)} 个内部链接")
            print(unvisied_links)
            self.queue.clear()
            if unvisied_links == []:
                break
            self.all_inner_urls = self.all_inner_urls.union(unvisied_links)

            num += 1
            if num > 1:
                break
            thread_num = len(unvisied_links) if len(unvisied_links) <= 500 else 500
            with ThreadPool(processes=thread_num) as executor:
                executor.map(self.get_innner_links, unvisied_links)

    def save_inner_links_of_single_site(self, url):
        self.all_inner_urls = self.all_inner_urls.union(
            self.get_innner_links(url))


# keywords = [
#     "揭发一个低素质政府工作人员",
#     "有没有地铁卡，我公公掉了一张",
#     "苏州农村商业银行",
#     "恶心的反胃",
#     "苏农银行",
#     "szrcb",
#     "wjrcb",
#     "吴江农付商业银行",
# ]

# for link in soup.find_all("a"):
#    if link.get("href") and link.get("href").startswith("thread"):
#        inner_urls.append(url + link.get("href"))
# return inner_urls

if __name__ == "__main__":
    keywords = ['吴江农商行', '苏州农商行', '苏州农村商业银行','太湖新城没有了',
                '苏农银行', 'szrcb', 'wjrcb', '吴江农付商业银行']
    begin = time.time()
    bbs = BbsMonitor('https://bbs.wjdaily.com/bbs/', keywords=keywords)
    bbs.get_all_innner_links()
    bbs_num = len(bbs.all_inner_urls)
    logger.info(f"获取不同的内部链接{bbs_num}个")
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
    all_inner_urls_list = list(bbs.all_inner_urls)
    asyncio.run(bbs.asyn_tasks(all_inner_urls_list))
    # while i < bbs_num:
    #     begin = i
    #     end = i + 500
    #     if end > bbs_num:
    #         end = bbs_num
    #     asyncio.run(bbs.asyn_tasks(bbs.all_inner_urls[begin,end]))
    end = time.time()
    logger.info(f"耗时 {end-begin} 秒")

    # 发送邮件
    message = {
        'subject': "东太湖论坛舆情监控",
        'message': f"在{bbs_num}个帖子中找到含有关键字{keywords}的网站有:\n{bbs.warn_urls}\n耗时{end-begin}秒",
        'from_email': 'zhengzheng@szrcb.com',
        'to_email': 'zhengzheng@szrcb.com'
    }
    logger.info(message)
