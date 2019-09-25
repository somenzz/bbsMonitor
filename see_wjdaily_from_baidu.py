# encoding=utf-8
from splinter import Browser
import time, os, sys
import logging
from bs4 import BeautifulSoup
from sendMail import  sendHtmlMail

current_path = sys.path[0]
os.chdir(current_path)
print(f"current path is {os.getcwd()}")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fh = logging.FileHandler(filename="bbsMonitor.log")
formatter = logging.Formatter('%(asctime)s - %(filename)s - line:%(lineno)d - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(ch)  # 将日志输出至屏幕
logger.addHandler(fh)  # 将日志输出至文件


class AutoSearch(object):
    def __init__(self):
        self.browser = None
        self.base_url = 'https://www.baidu.com/'
        self.keywords = ['高压线下也敢飞','珍惜现在的好天气吧']
        self.keywords_pngs = []

    def send_png(self):
        '''
         发送邮件，此函数请自行实现
        :return:
        '''
        sendHtmlMail(self.keywords_pngs)

    def search(self,time_freq = "一天内"):
        self.browser = Browser(driver_name='chrome', executable_path='chromedriver.exe')
        self.browser.visit(self.base_url)
        for word in self.keywords:
            kw = f'+"{word}" site:bbs.wjdaily.com'
            if self.browser.is_element_present_by_id("kw"):
                self.browser.find_by_id("kw").fill(kw)
                time.sleep(1)
                self.browser.find_by_id("su").click()
                # self.browser.find_by_xpath('//*[@id="container"]/div[2]/div/div[1]/span[2]').first.click()
                time.sleep(1)
                if self.browser.is_element_present_by_css(".search_tool_tf",wait_time=10):
                    self.browser.find_by_css(".search_tool_tf").first.click()
                if self.browser.is_element_present_by_text(time_freq):
                    self.browser.click_link_by_text(time_freq)
                time.sleep(3)
                soup = BeautifulSoup(self.browser.html,"html.parser")
                no_result = soup.find('div',{'class':'nors'})
                if no_result is None:
                    print("查到结果，截图")
                    screenshot_path = self.browser.screenshot(rf"E:\GitHub\somenzz\bbsMonitor\{word}",suffix=".png")
                    self.keywords_pngs.append(screenshot_path)


if __name__ == '__main__':
    autoSearch  = AutoSearch()
    autoSearch.search("一周内")
    if autoSearch.keywords_pngs != []:
        autoSearch.send_png()
    autoSearch.browser.quit()
