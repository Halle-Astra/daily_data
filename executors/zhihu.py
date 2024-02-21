# print(__name__) # executors.zhihu
# print(vars())
from clients.requests_client import Client as RqClient
from loguru import logger
from .core import BaseExecutor

class  Executor_v1(BaseExecutor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rq_client = RqClient(**kwargs)
        self.rq_client.login()

        self.base_url=kwargs['base_url']
        logger.info(self.base_url)

    #def get_home(self):
    def __call__(self):
        super().run_primary()

    def start(self):
        self.__call__()
