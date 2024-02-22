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
            answer_sample = dict(question={})
            answer_url = answer_url[2:]
            question_id = answer_url.split('/')[-3]
            answer_id = answer_url.split('/')[-1]

            answer_url = 'https://' + answer_url
            answer_r = self.rq_client.get(answer_url)
            if answer_r.status_code == 200:
                answer_r.encoding = answer_r.apparent_encoding
                answer_html = etree.HTML(answer_r.text)
                answer_init_json = answer_html.xpath('//script[@id="js-initialData"]/text()')
                if len(answer_init_json) != 1:
                    logger.warning('The number of answer information is not 1!')
                else:
                    answer_init_json = answer_init_json[0]
                    answer_init_json = json.loads(answer_init_json)

                    if answer_init_json['spanName'] == 'AnswerPage':
                        answer_sample['content_type'] = 'answer'

                        question_json = answer_init_json['initialState']['entities']['questions'][question_id]
                        question_title = question_json['title']
                        question_content = question_json['editableDetail']
                        question_topics = question_json['topics']
                        logger.debug('question content is {}'.format(question_content))

                        answer_sample['question_verbose_json'] = question_json
                        answer_sample['question'] = dict(
                            title=question_title,
                            content=question_content,
                            topics=question_topics,
                            id=question_id
                        )

                        answer_entity = answer_init_json['initialState']['entities']['answers'][answer_id]
                        answer_simple = dict(
                            content = answer_entity['content'],
                            answer_id = answer_id,
                        )
                        answer_sample['answer'] = answer_simple
                        answer_sample['answer_verbose_json'] = answer_entity
                        answer_sample['original_json'] = answer_init_json


    def start(self):
        self.__call__()
