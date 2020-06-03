import json
from pyquery import PyQuery as pq
import requests
import re
import aiohttp
import asyncio
from lxml import etree
import time
from threading import Thread


class ProxyMetaclass(type):
    def __new__(cls, name, base, attrs, *args, **kwargs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return super().__new__(cls, name, base, attrs, *args, **kwargs)


class Crawler(metaclass=ProxyMetaclass):
    async def get_proxies(self, callback):
        res = await asyncio.gather(eval("self.{0}()".format(callback)))
        return res[0]

    async def get_page(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        }
        # proxy = 'http://' + self.get_proxy()
        proxy = None
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers, proxy=proxy) as resp:
                return await resp.text()

    # 66代理api
    async def crawl_daili66_api(self):
        async def crawl_single_url(url):
            page = await self.get_page(url)
            if page:
                items = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{1,5}', page, re.S)
                res.extend(items)

        start_url = 'http://www.66ip.cn/nmtq.php?getnum=&isp=0&anonymoustype={type}&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip'
        urls = [start_url.format(type=t) for t in [3, 4]]
        res = []
        tasks = []
        for url in urls:
            for t in range(3):
                print('[*] Crawling: ', url)
                tasks.append(crawl_single_url(url))
        await asyncio.gather(*tasks)
        return res

    async def crawl_daili66(self):
        # 爬取单个url
        async def crawl_single_url(url):
            page = await self.get_page(url)
            if page:
                html = etree.HTML(page)
                ip = html.xpath('//div[@align="center"]/table/tr[position()>1]/td[position()<3]/text()')
                for i in range(0, len(ip) - 2, 2):
                    res.append(str(ip[i]) + ':' + str(ip[i + 1]))

        start_url = 'http://www.66ip.cn/{page}.html'
        urls = [start_url.format(page=p) for p in range(1, 5)]
        res = []
        tasks = []
        for url in urls:
            print('[*] Crawling: ', url)
            tasks.append(crawl_single_url(url))
        await asyncio.gather(*tasks)
        return res

    # 西刺代理
    async def crawl_xichi(self):
        async def crawl_single_url(url):
            page = await self.get_page(url)
            if page:
                html = etree.HTML(page)
                ip = html.xpath('//tr/td[position() > 1 and position() < 4]/text()')
                for i in range(0, len(ip) - 2, 2):
                    res.append(str(ip[i]) + ':' + str(ip[i + 1]))

        start_url = 'https://www.xicidaili.com/nn/{page}'
        urls = [start_url.format(page=p) for p in [1, 2]]
        res = []
        tasks = []
        for url in urls:
            print('[*] Crawling: ', url)
            tasks.append(crawl_single_url(url))
        await asyncio.gather(*tasks)
        return res

    # 快代理
    # 网站设置了1秒间隔，不支持无代理的异步并发
    async def crawl_kuaidaili(self):
        start_url = 'http://www.kuaidaili.com/free/inha/{page}/'
        urls = [start_url.format(page=p) for p in range(1, 5)]
        res = []
        for url in urls:
            print('[*] Crawling: ', url)
            page = await self.get_page(url)
            if page:
                # time.sleep(3)
                html = etree.HTML(page)
                ip = html.xpath('//tr/td[position() < 3]/text()')
                for i in range(0, len(ip) - 2, 2):
                    res.append(str(ip[i]) + ':' + str(ip[i + 1]))
            time.sleep(1)
        return res

    # 云代理
    async def crawl_kuaidaili(self):
        async def crawl_single_url(url):
            page = await self.get_page(url)
            if page:
                # time.sleep(3)
                html = etree.HTML(page)
                ip = html.xpath('//tbody/tr/td[position() <3]/text()')
                for i in range(0, len(ip) - 2, 2):
                    res.append(str(ip[i]) + ':' + str(ip[i + 1]))

        start_url = 'http://www.ip3366.net/?stype=1&page={page}'
        urls = [start_url.format(page=p) for p in range(1, 6)]
        res = []
        tasks = []
        for url in urls:
            print('[*] Crawling: ', url)
            tasks.append(crawl_single_url(url))
        await asyncio.gather(*tasks)
        return res

    # 代理中国
    # 网站设置了同一ip同一时间只能发送三个请求。
    # 将并发设置成3个一组
    async def crawl_kuaidaili(self):
        async def crawl_single_url(url):
            page = await self.get_page(url)
            if page:
                html = etree.HTML(page)
                ip = html.xpath('//tbody/tr/td[position()<3]/text()')
                for i in range(0, len(ip) - 2, 2):
                    res.append(str(ip[i]) + ':' + str(ip[i + 1]))

        start_url = 'https://ip.jiangxianli.com/?page={page}&anonymity=2'
        urls = [start_url.format(page=p) for p in range(1, 12)]
        res, tasks = [], []
        for url in urls:
            print('[*] Crawling: ', url)
            tasks.append(crawl_single_url(url))
        # await asyncio.wait(tasks)
        # 设置3个一组并发
        interval = 3
        for j in range(0,len(tasks),interval):
            await asyncio.wait(tasks[j:j+interval])
            await asyncio.sleep(1)
        return res

    def get_proxy(self):
        return requests.get('http://127.0.0.1:5000/random').text


if __name__ == '__main__':
    c = Crawler()
    res = asyncio.run(c.get_proxies("crawl_kuaidaili"))
    print(len(res),res)
