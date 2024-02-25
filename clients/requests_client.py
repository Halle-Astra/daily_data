import os.path

import requests as rq
from utils import read_json
import time
from loguru import logger
from utils import url_toolkit

HEADERS_PATH = './configs/headers.json'
ATTEMPT = 3


# base_headers =

class Client:
    def __init__(self, base_url,
                 login_path=None,
                 cookies=None,
                 name="non-name",
                 sleep_time=5,
                 **kwargs):
        self.client = rq.session()

        if cookies is not None :
            self.set_cookies(cookies)
            self.init_cookies = cookies

        self.client.encoding = 'utf-8'

        self.endpoint = base_url
        self.login_path = login_path

        # 这个最好就不要做改变了
        self.base_headers = read_json(HEADERS_PATH)
        self.name = name
        self.logger = logger # 暂时保留自定义logger实现的可能，如果需要开放自定义logger实现，则将loguru.logger赋予别名loguru_logger, 然后传递一个可选参数logger=None做判断即可
        self.sleep_time = sleep_time

        # 这个允许进行值的改变
        self.headers = read_json(HEADERS_PATH)

    def set_cookies(self, cookies):
        if os.path.exists(cookies['session_cookie']):
            c_f = open(cookies['session_cookie'])
            cookies['session_cookie'] = c_f.read()
            c_f.close()

            self.init_cookies = cookies

        # set cookies
        if cookies is not None:
            for key in cookies:
                self.client.cookies.set(key, cookies[key])

    def login(self):
        if self.login_path is None:
            self.logger.error("RQ客户端{} :未配置登录地址，故本次登录指令无效，将停止登录操作".format(self.name))
            return
        # login_url = self.endpoint + self.login_path
        login_url = url_toolkit.join(self.endpoint, self.login_path)
        login_header = self.headers
        login_header['Referer'] = login_url

        for try_cnt in range(ATTEMPT):
            self.client.get(login_url)
            result = self.client.post(
                login_url, headers=login_header
            )

            # result.url 判断是否真正登录成功
            if result.ok and result.url != login_url:# self.endpoint:
                self.logger.info("Login successfully!")
                # f = open('temp.html', 'w', encoding='utf-8')
                # f.write(result.text)
                # f.close()
                return
            self.logger.warning("Login failed, Wait till next round!")
            if try_cnt != ATTEMPT - 1:
                time.sleep(self.sleep_time)

        self.logger.error(
            "LoginError: Login failed, ensure your login credential is correct!"
        )

    def get(self, url, headers=None, set_referer=False, **kwargs):
        if headers is None:
            headers = self.headers
        if headers is not None:
            kwargs['headers'] = headers
        # logger.info('the headers are: \n{}\n, and the kwargs are:\n{} '.format(headers,kwargs))
        response = self.client.get(url, **kwargs)
        if set_referer:
            self.headers['Referer'] = url
        return response

    def post(self, url, headers=None, set_referer=False, **kwargs):
        if headers is None:
            headers = self.headers
        if headers is not None:
            kwargs['headers'] = headers
        response = self.client.post(url, **kwargs)
        if set_referer:
            self.headers['Referer'] = url
        return response
