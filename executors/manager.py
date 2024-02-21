from utils import read_json
from loguru import logger

SITES_CONFIG = "configs/sites.json"

class Manager:
    def __init__(self):
        self.init()

    def init(self):
        sites_configs = read_json(SITES_CONFIG)
        self.must_sites = []
        self.relax_sites = []

        def init_group(group_name, group):
            group_config = sites_configs[group_name]
            for site_name in group_config.keys():
                executor_class_info = group_config[site_name]['executor']
                executor_module, executor_class = executor_class_info.split('.')
                # print(__package__)
                # 关于fromlist参数，我只能说，很离谱，详见README的Reference
                site_package = __import__('{}.{}'.format(__package__, executor_module),fromlist=True)
                site_class = getattr(site_package, executor_class)
                site_executor = site_class(**group_config[site_name])
                group.append(site_executor)
                logger.info("The site {} has been initiated as {}".format(
                    site_name, executor_class_info
                ))
        init_group('must', self.must_sites)
        init_group('relax', self.relax_sites)
        logger.info('Site groups initiated. Fixed sites has {}. Relaxing sites has {}'.format(
            len(self.must_sites), len(self.relax_sites)
        ))

    def group_start(self, group):
        for executor in group:
            executor.start()


    def start(self):
        self.group_start(self.must_sites)
        self.group_start(self.relax_sites)


