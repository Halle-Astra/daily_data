def url_part_clean(part):
    """此接口暂不实现，需要了解更多的url规范才能确定有哪些东西是肯定不会出现的，
    目前先假设用户不会搞事情，以及用户只会出现一条杠两条杠的问题，而两条杠的问题不需要我们去管"""
    # part = part.replace('/')
    return part


def split_prefix(url):
    prefix = ''
    if url.startswith("http://"):
        http_start = True
        prefix = 'http://'
    if url.startswith('https://'):
        https_start = True
        prefix = 'https://'
    if prefix:
        url_main = url.lstrip(prefix)
    return prefix, url_main


def unify(url, must_prefix=True):
    prefix, url_main = split_prefix(url)
    if must_prefix and prefix=='':
        prefix = 'http://'
    url_main_ls = url_main.split('/')
    url_main_ls = [url_part_clean(i) for i in url_main_ls if i]
    url_main = '/'.join(url_main_ls)
    url_unified = prefix + url_main
    return url_unified


def join(*args):
    url = '/'.join(args)
    url = unify(url)
    return url
