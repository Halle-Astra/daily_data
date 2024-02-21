# print(__name__) # executors.zhihu
# print(vars())
from clients.requests_client import Client as RqClient
from loguru import logger
from .core import BaseExecutor
from lxml import etree

class  Executor_v1(BaseExecutor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rq_client = RqClient(**kwargs)
        self.rq_client.login()

        self.base_url=kwargs['base_url']
        logger.info(self.base_url)

    #def get_home(self):
    def __call__(self):
        answer_urls = super().run_primary()
        for answer_url in answer_urls:
            answer_url = answer_url[2:]
            question_url = 'https://' + '/'.join(answer_url.split('/')[:3])
            question_init_web = self.rq_client.get(question_url)
            if question_init_web.status_code == 200:
                question_init_web.encoding = question_init_web.apparent_encoding
                q_init_html = etree.HTML(question_init_web.text)
                q_info = q_init_html.xpath('//script[@id="js-initialData"]/text()') # 会得到一大堆东西
                logger.info(q_info )




    def start(self):
        self.__call__()
