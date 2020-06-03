import sys

sys.path.append('../')
from storage.redisclient import RedisClient
import asyncio
import aiohttp
from setting import VALID_STATUS_CODES, TEST_URL, BATCH_TEST_SIZE, TEST_TIME_OUT
import time


class Tester:
    def __init__(self):
        self.client = RedisClient()

    async def test_single_proxy(self, proxy):
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            }
            http_proxy = 'http://' + proxy
            print("[*] testing: {}".format(proxy))
            try:
                async with session.get(url=TEST_URL, headers=headers, proxy=http_proxy, timeout=TEST_TIME_OUT) as resp:
                    status_code = resp.status
                    if status_code in VALID_STATUS_CODES:
                        print("[*] {} available...".format(proxy))
                        self.client.setmax(proxy)
                    else:
                        self.client.decrease(proxy)
                        print('[*] {} disavailable...'.format(proxy))
            except Exception as e:
                self.client.decrease(proxy)
                print("[!] testing {} err: {}".format(proxy, e))

    def run(self):
        try:
            proxies = self.client.getall()
            loop = asyncio.get_event_loop()
            for i in range(0, len(proxies), BATCH_TEST_SIZE):
                test_proxies = proxies[i: i + BATCH_TEST_SIZE]
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                time.sleep(5)
        except Exception as e:
            print('[!] Tester errors !!!', e.args)


if __name__ == '__main__':
    t = Tester()
    t.run()
