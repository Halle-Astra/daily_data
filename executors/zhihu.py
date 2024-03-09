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
import time
from .core import antispider


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

    def get_comments(self, target_id, limit=20, referer='', target_type='answer'):
        """

        :param target_id:
        :param limit:
        :param referer:
        :param target_type: Optional: ['answer', 'article']
        :return:
        """

        def get_childs(comment):
            child_url_template = 'https://www.zhihu.com/api/v4/comment_v5/comment/<comment_id>/child_comment?order_by=ts&limit=20&offset='
            childs_num = comment['child_comment_count']
            c_id = comment['id']
            child_comments = []

            if childs_num == 0:
                return child_comments

            child_url = child_url_template.replace('<comment_id>', str(c_id))
            break_flag = False
            while not break_flag:
                try_cnt = 0
                max_try = 3
                while True:  # 这部分之后再统一为try的装饰器
                    child_comments_r = self.rq_client.get(child_url)
                    if child_comments_r.status_code == 200:
                        child_comments_json = child_comments_r.json()
                        c_ls = child_comments_json['data']
                        child_comments.extend(c_ls)

                        is_end = child_comments_json['paging']['is_end']
                        if is_end:
                            break_flag = True
                        else:
                            child_url = child_comments_json['paging']['next']
                        break

                    else:
                        try_cnt += 1
                        logger.warning("当前子评论获取失败{}, 将睡眠5秒后重新尝试{}/{}".format(
                            child_url, try_cnt, max_try
                        ))
                    if try_cnt == max_try:
                        break
            return child_comments

        root_comments_url = f'https://www.zhihu.com/api/v4/{target_type}s/{target_id}/root_comments?limit=20&offset=&order_by=normal'
        # first_comments = self.rq_client.get(root_comments_url)

        comments_pack = dict()
        first_flag = True
        while True:
            try:
                comments = self.rq_client.get(root_comments_url).json()
            except:
                break
            # common_counts = comments['common_counts']
            root_comments_num = len(comments['data'])

            # comments_json = {}
            for i in range(root_comments_num):
                comments['data'][i]['childs'] = get_childs(
                    comments['data'][i]
                )

            if first_flag:
                comments_pack = comments
                first_flag = False
            else:
                comments_pack['data'].extend(comments['data'])

            is_end = comments['paging']['is_end']
            if not is_end:
                root_comments_url = comments['paging']['next']
            else:
                break

            logger.debug('answer_comments of  {} are\n{}'.format(root_comments_url, comments))
            # logger.debug('headers is {}'.format(headers))
        return comments

    def process_answer_url(self, answer_url):
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
                    answer_sample['comments'] = self.get_comments(
                        answer_id,
                        referer=answer_url,
                        target_type='answer'
                    )
        return answer_sample

    def detect_type_from_recommendation_url(self, url):
        url = url[2:]
        url_comps = url.split('/')
        if url_comps[0] == 'www.zhihu.com' and url_comps[1] == 'question' \
                and url_comps[3] == 'answer':
            url_type = 'answer'
        elif url_comps[0] == 'zhuanlan.zhihu.com':
            url_type = 'article'
        else:
            url_type = 'unknown'
        return url_type

    # def get_home(self):
    @antispider
    def __call__(self):
        recommendation_urls = super().run_primary()

        contents = []
        for recommendation_url in recommendation_urls:
            url_type = self.detect_type_from_recommendation_url(recommendation_url)
            if url_type == 'answer':
                answer_content = self.process_answer_url(recommendation_url)
                contents.append(answer_content)
            pass
        f = open('output.jsonl', 'a', encoding='utf-8')
        contents = [json.dumps(i, ensure_ascii=False) for i in contents]
        f.write('\n'.join(contents))
        f.close()

    def start(self):
        while True:
            try:
                self.__call__()
            except:
                logger.error("出现错误，可能被反爬了，将跳过此次爬取")
