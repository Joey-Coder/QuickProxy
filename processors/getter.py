from QuickProxy.storage import redisclient
from QuickProxy.crawler import crawler
from setting import POOL_UPPER_THRESHOLD
import asyncio


class Getter:
    def __init__(self):
        self.client = redisclient.RedisClient()
        self.crawler = crawler.Crawler()

    def is_over_threshold(self):
        if self.client.getcount() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False

    async def run(self):
        if not self.is_over_threshold():
            threads = []
            # loop = asyncio.get_event_loop()
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callback_label]
                threads.append(self.crawler.get_proxies(callback))

            # proxies = loop.run_until_complete(asyncio.gather(*threads))
            proxies = await asyncio.gather(*threads)
            count = 0
            for website in proxies:
                for proxy in website:
                    self.client.add(proxy)
                    # 保证这里的格式是ip:port
                    print("[*] crawl {}".format(proxy))
                    count +=1
            print("[*] get {} proxy...".format(count))

if __name__ == '__main__':
    g = Getter()
    asyncio.run(g.run())
