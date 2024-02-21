from executors import Manager

# 这个初始化，改交给utils.__init__自己完成
# from utils.log import init_logger
#
# init_logger()

manager = Manager()
manager.start()
