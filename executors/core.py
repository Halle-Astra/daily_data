from clients.requests_client import Client as RqClient
from loguru import logger
from easydict import EasyDict
from utils import url_toolkit
from lxml import etree
from functools import wraps
import random
import time

class AntiSpiderExecutor:
    def __init__(self, min_sleep=1, max_sleep=30):
        self.min_sleep=min_sleep
        self.max_sleep=max_sleep
        pass

    def do_anti(self):
        t = random.randint(self.min_sleep, self.max_sleep)
        logger.debug("为防止反爬，将睡眠{}秒".format(t))
        time.sleep(t)

    def __call__(self, func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            self.do_anti()
            pass

            res = func(*args, **kwargs)
            return res

        return wrapped_func


# To normalize the style of api. So you can use the decorator with the name in lowercase.
# Of course, you can also use the decorator in class form if you like it.
antispider = AntiSpiderExecutor()


class Timer:
    def __init__(self):
        pass


class BaseSuccessCheck:
    """此类调用时，会调用check方法，因此用于只需要继承此类，然后重写check方法就好了
    因此可以在check中进行一些cookies调整等方案，以纠正爬取参数"""

    def __init__(self):
        pass

    def __call__(self, result):
        return self.check(result)

    def check(self, result):
        """如果用户不重写此方法，那么就会直接返回，对于TryClass而言，就是直接不重试"""
        return True


class TryClass:
    def __init__(self, times, success_check=None):
        self.times = times
        self.success_check = success_check
        if success_check is None:
            self.success_check = BaseSuccessCheck()

    def __call__(self, func):
        """实现多次尝试，可以对访问网址进行尝试，也可以是其他各类函数的多次尝试"""

        @wraps(func)
        def wrapped(*args, **kwargs):
            for i in range(self.times):
                result = func(*args, **kwargs)
                flag = self.success_check(result)
                if flag:
                    return result
                else:
                    logger.warning(
                        "The assignment of {} is failed and will be tried before the final trying. {}/{}".format(
                            func, i + 1, self.times
                        ))

            # Though this result will be helpless.
            # In fact, we advise the developer do the success_check after getting result to make the code can be
            # maintained easily.
            return result

        return wrapped

    def go(self, func):
        return self.__call__(func)


def run_and_retry(times, success_check=None):
    """This function is designed with TryClass to unify the style of api."""
    logger.info("decorate in run_and_retry")
    def retry_instantiated(func):
        try_object = TryClass(times, success_check)
        return try_object(func)

    return retry_instantiated


class BaseExecutor:
    def _check_args(self, **kwargs):
        '''check kwargs in dict form and return in the same form'''
        url = url_toolkit.unify(kwargs['base_url'])
        kwargs['base_url'] = url
        return kwargs

    def __init__(self, **kwargs):
        kwargs = self._check_args(**kwargs)
        self.rq_client = RqClient(**kwargs)

        # 利用login_path来判断是否需要登录，默认为None
        self.base_url = kwargs['base_url']
        self.login_path = kwargs['login_path']

        # 转为易用数据类型并存储
        self.params = EasyDict(kwargs)

        # 假设存在登录的链接，则启用登录功能，并登录
        self.enable_login = False
        if kwargs['login_path'] is not None and kwargs['login_path'].lstrip('./'):
            self.enable_login = True
            self.rq_client.login()

    def primary_subtask(self, ):
        pass

    # @run_and_retry(3)
    def run_primary(self):
        """最主要的，一个网站必须要有的任务，也就是要满足的基本爬虫功能，一个常规简单爬虫任务通常会有的想法"""
        p_info = self.params.targets.primary
        p_url = url_toolkit.join(self.base_url, p_info['path'])
        # subtasks = p_info['candidates_info']
        # grades = len(subtasks)
        response = self.rq_client.get(p_url, headers=self.rq_client.headers)
        if response.status_code != 200:
            logger.error("Primary request of {} returned with error code {}".format(
                p_url, response.status_code
            ))
            # exit(0)
        else:
            response.encoding = response.apparent_encoding
            html = etree.HTML(response.text)
            xpath_string = p_info['candidates_info']['value']
            result = html.xpath(xpath_string)
            logger.info("result: {}".format(result))
            if result:
                # logger.info(result)
                return result
            else:
                logger.error("No any result of primary task. result: {}".format(result))
                return result
