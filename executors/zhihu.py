# print(__name__) # executors.zhihu
# print(vars())
from clients.requests_client import Client as RqClient
from loguru import logger
from .core import BaseExecutor
from lxml import etree
import json


class Executor_v1(BaseExecutor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rq_client = RqClient(**kwargs)
        self.rq_client.login()

        self.base_url = kwargs['base_url']
        logger.info(self.base_url)

    # def get_home(self):
    def __call__(self):
        answer_urls = super().run_primary()
        for answer_url in answer_urls:
            answer_url = answer_url[2:]
            question_id = answer_url.split('/')[-3]

            answer_url = 'https://'+answer_url
            answer_r = self.rq_client.get(answer_url)
            if answer_r.status_code==200:
                answer_r.encoding = answer_r.apparent_encoding
                answer_html = etree.HTML(answer_r.text)
                answer_init_json = answer_html.xpath('//script[@id="js-initialData"]/text()')
                if len(answer_init_json) != 1:
                    logger.warning('The number of answer information is not 1!')
                else:
                    answer_init_json = answer_init_json[0]
                    answer_init_json = json.loads(answer_init_json)
                    question_json = answer_init_json['initialState']['entities']['questions'][question_id]
                    question_title = question_json['title']
                    question_content = question_json['editableDetail']
                    question_topics = question_json['topics']
                    logger.info('question content is {}'.format(question_content))


            # 最后分析发现，问题的细节本身在answer的页面里能找到
            # question_url = 'https://' + '/'.join(answer_url.split('/')[:3])
            # question_init_web = self.rq_client.get(question_url)
            # if question_init_web.status_code == 200:
            #     question_init_web.encoding = question_init_web.apparent_encoding
            #     q_init_html = etree.HTML(question_init_web.text)
            #     q_info = q_init_html.xpath('//script[@id="js-initialData"]/text()')  # 会得到一大堆东西
            #     if len(q_info) != 1:
            #         logger.warning('The number of question information is not 1!')
            #     else:
            #         q_info = q_info[0]
            #         q_info = json.loads(q_info)
            #     logger.info(q_info)

    def start(self):
        self.__call__()
