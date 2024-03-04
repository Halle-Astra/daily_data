# print(__name__) # executors.zhihu
# print(vars())
from clients.requests_client import Client as RqClient
from loguru import logger
from .core import BaseExecutor
from lxml import etree
import json
import execjs
import base64
import hashlib


class Zse96:
    def __init__(self):
        self.f_helper = self.init()

    def init(self, js_code='js/zse96v2.js'):
        with open(js_code, encoding='utf-8') as f:
            js_code = f.read()
        ctx = execjs.compile(js_code, cwd='js')
        return ctx

    def __call__(self, url, v):
        urlp = url.split('https://www.zhihu.com')[1]
        string_composed = '+'.join(["101_3_3.0", urlp, v])
        v_md5 = hashlib.md5(string_composed.encode()).hexdigest()
        res = self.f_helper.call("encrypt_core", v_md5)
        res = base64.b64encode(res.encode()).decode()
        logger.debug('the result of x-zse-96 is {}'.format(res))
        return res

zse96 = Zse96()

class Executor_v1(BaseExecutor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rq_client = RqClient(**kwargs)
        self.rq_client.login()

        self.base_url = kwargs['base_url']
        logger.info(self.base_url)

    def get_answer_comments(self, answer_id, limit=20, referer=''):
        # template = 'https://www.zhihu.com/api/v4/comment_v5/answers/3398863180/root_comment?order_by=score&limit=20&offset='
        template = f'https://www.zhihu.com/api/v4/comment_v5/answers/{answer_id}/root_comment?order_by=score&limit=20&offset='
        headers = {}
        for key in self.rq_client.headers:
            headers[key] = self.rq_client.headers[key]
        if referer:
            headers['Referer'] = referer
        headers['cookie'] = self.rq_client.init_cookies['session_cookie']
        def extract_d_c0(c):
            cs = c.split(';')
            for ii in cs:
                ii_split = ii.split('=')
                if ii_split[0].strip()=="d_c0":
                    return ii_split[1]+'='+ii_split[2]

        headers['x-requested-with'] = 'fetch'
        headers['x-zse-93'] = '101_3_3.0'
        headers['x-zse-96'] = '2.0_' + zse96(template, extract_d_c0(headers['cookie']))
        answer_comments = self.rq_client.get(template, headers=headers).json()
        logger.debug('answer_comments of  {} are\n{}'.format(template, answer_comments))
        logger.debug('headers is {}'.format(headers))

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
                            content=answer_entity['content'],
                            answer_id=answer_id,
                        )
                        answer_sample['answer'] = answer_simple
                        answer_sample['answer_verbose_json'] = answer_entity
                        answer_sample['original_json'] = answer_init_json
                        self.get_answer_comments(answer_id, referer=answer_url)

    def start(self):
        self.__call__()
