import requests
import re, time
from bs4 import BeautifulSoup
import threading
from multiprocessing.dummy import Pool as ThreadPool
import zmail
# 定义全局变量
all_urls = set()
warn_urls = []
# keywords = ['吴江农商行', '苏州农商行', '苏州农村商业银行','苏农银行', 'szrcb', 'wjrcb', '吴江农付商业银行']
keywords = [
    "揭发一个低素质政府工作人员",
    "有没有地铁卡，我公公掉了一张",
    "恶心的反胃",
]


def isWarningUrl(url):
    """
    判断一个网站的内容是否有关键词
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
    }
    reg = re.compile("|".join(keywords))
    try:
        r = requests.get(url, headers=headers)
        if re.findall(reg, r.text):
            warn_urls.append(url)
            return True
        return False
    except:
        pass
    return False


def get_bbs_urls(url="https://bbs.wjdaily.com/bbs/"):
    """
    获取论坛网站所有的链接
    """
    if url not in all_urls:
        all_urls.add(url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
    }

    r = requests.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href")
        if href is None:
            continue
        if href.startswith("https://bbs.wjdaily.com/bbs/"):
            if href not in all_urls:
                all_urls.add(href)
                get_bbs_urls(href)
        elif href.startswith("http"):
            pass
        else:
            href = "https://bbs.wjdaily.com/bbs/" + href
            if href not in all_urls:
                all_urls.add(href)
                get_bbs_urls(href)

    #for link in soup.find_all("a"):
    #    if link.get("href") and link.get("href").startswith("thread"):
    #        inner_urls.append(url + link.get("href"))
    #return inner_urls


if __name__ == "__main__":
    begin = time.time()
    get_bbs_urls()
    end = time.time()
    
    print(len(all_urls))
    print(f"耗时{end-begin}s")
    exit(0)
    num = len(all_urls)
    print(num)

    with ThreadPool(processes=num) as executor:
        executor.map(isWarningUrl, inner_urls)

    end = time.time()
    print(warn_urls)
    print(f"耗时{end-begin}s")






from urllib.request import urlopen from bs4 import BeautifulSoup import re import datetime import random pages = set() random.seed(datetime.datetime.now()) # 获取页面所有内链的列表def getInternalLinks(bsObj, includeUrl):     internalLinks = []     # 找出所有以"/"开头的链接for link in bsObj.findAll("a", href=re.compile("^(/|.*"+includeUrl+")")): if link.attrs['href'] is not None: if link.attrs['href'] notin internalLinks:                 internalLinks.append(link.attrs['href']) return internalLinks # 获取页面所有外链的列表def getExternalLinks(bsObj, excludeUrl):     externalLinks = []     # 找出所有以"http"或"www"开头且不包含当前URL的链接for link in bsObj.findAll("a",                           href=re.compile("^(http|www)((?!"+excludeUrl+").)*$")): if link.attrs['href'] is not None: if link.attrs['href'] not in externalLinks:                 externalLinks.append(link.attrs['href']) return externalLinks def splitAddress(address):     addressParts = address.replace("http://", "").split("/") return addressParts def getRandomExternalLink(startingPage):     html = urlopen(startingPage)     bsObj = BeautifulSoup(html)     externalLinks = getExternalLinks(bsObj, splitAddress(startingPage)[0]) if len(externalLinks) == 0:         internalLinks = getInternalLinks(startingPage) return getNextExternalLink(internalLinks[random.randint(0,                                    len(internalLinks)-1)]) else: return externalLinks[random.randint(0, len(externalLinks)-1)] def followExternalOnly(startingSite):     externalLink = getRandomExternalLink("http://oreilly.com") print("随机外链是："+externalLink)    followExternalOnly(externalLink)followExternalOnly("http://oreilly.com")
