import platform
import requests
import json
import os
import time
from datetime import datetime

from jd_seckill.jd_logger import logger

if __name__ == '__main__':
    if platform.system() == 'Linux':
        url = 'https://a.jd.com//ajax/queryServerData.html'
        session = requests.session()
        # get server time
        t0 = datetime.now()
        ret = session.get(url).text
        t1 = datetime.now()

        js = json.loads(ret)
        t = float(js["serverTime"]) / 1000
        dt = datetime.fromtimestamp(t) + ((t1 - t0) / 2)
        tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.localtime(
            time.mktime(dt.timetuple()))
        server_time = '{}-{}-{} {}:{}:{}.{}'.format(tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, dt.microsecond)
        os.system(
            "date -s '{}'".format(server_time))
        logger.info('同步服务器时间：%s', server_time)
