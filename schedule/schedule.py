import sys

sys.path.append('../')

from multiprocessing import Process
from export.api import app
from processors.getter import Getter
from tester.tester import Tester
from setting import TESTER_CYCLE, GETTER_CYCLE, TESTER_ENABLED, GETTER_ENABLED, API_ENABLED, API_HOST, API_PORT, \
    GETTER_FLAG, GETTER_MAX
import time


class Scheduler:
    def schedule_tester(self, cycle=TESTER_CYCLE):
        tester = Tester()
        while True:
            if tester.client.getavailcount() < GETTER_FLAG:
                print('[+] Tester start runing...')
                tester.run()
                time.sleep(cycle)

    def schedule_getter(self, cycle=GETTER_CYCLE):
        getter = Getter()
        while True:
            if getter.client.getavailcount() < GETTER_FLAG and getter.client.getcount() < GETTER_MAX:
                print('[+] Getter start runing...')
                getter.run()
                time.sleep(cycle)

    def schedule_api(self):
        app.run(host=API_HOST, port=API_PORT)

    def run(self):
        print("[+] QuickProxy start....")
        if API_ENABLED:
            api_process = Process(target=self.schedule_api)
            api_process.start()
        if GETTER_ENABLED:
            getter_process = Process(target=self.schedule_getter)
            getter_process.start()
        if TESTER_ENABLED:
            tester_process = Process(target=self.schedule_tester)
            tester_process.start()


if __name__ == '__main__':
    s = Scheduler()
    s.run()
