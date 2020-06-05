import redis
from random import choice
from QuickProxy.setting import REDIS_HOST, REDIS_PASSWD, REDIS_PORT, MIN_SCORE, MAX_SCORE, INITIAL_SCORE, REDIS_KEY


class RedisClient:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, passwd=REDIS_PASSWD):
        '初始化生成redis connection'
        self.db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWD, decode_responses=True)

    def add(self, proxy, score=INITIAL_SCORE):
        '添加proxy到有序集合'
        if not self.db.zscore(REDIS_KEY, proxy):
            return self.db.zadd(REDIS_KEY, score, proxy)

    def random(self):
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)
            if len(result):
                return choice(result)
            else:
                raise Exception("90-100 proxy in {0} empty!".format(REDIS_KEY))

    def decrease(self, proxy):
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('[-] {proxy}: {score} - 1 = {cursore}'.format(proxy=proxy, score=score, cursore=score - 1))
            return self.db.zincrby(REDIS_KEY, proxy, -1)
        else:
            print('[-] remove {proxy}'.format(proxy=proxy))
            self.db.zrem(REDIS_KEY, proxy)

    def exists(self, proxy):
        return not self.db.zscore(REDIS_KEY, proxy) == None

    def setmax(self, proxy):
        print('[+] add {proxy}: {score}'.format(proxy=proxy, score=MAX_SCORE))
        self.db.zadd(REDIS_KEY, MAX_SCORE, proxy)

    def getcount(self):
        return self.db.zcard(REDIS_KEY)

    def getall(self):
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)

    # 获取分数为100的proxy数量
    def getavailcount(self):
        return self.db.zcount(REDIS_KEY, MAX_SCORE, MAX_SCORE)
