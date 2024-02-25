# daily_data
本项目的存在主要是为了每天都从一部分网站获得数据，构造数据集，包括固定的优质网站，以及随机网站两部分。



## 模块说明

### BaseExecutor

后续设计上来讲，可能primary也还是要改成列表的形式来进行探索了，基于requests的方案，无法提供完整的页面渲染，必须手动分析好所有的接口以获取数据

最后是只考虑一个大的入口，但是这个入口支持不同种类的xpath
1. scratch and access
2. click
3. scratch
4. post （估计没法用）

出于难度考虑，这里还是放弃了，还是单独从primary页面获取主要的candidates待爬子页面好了。

如果要考虑一种足够灵活的，其实还就是那种拼接模块的可视化方案会比较好，容易图形结合着促进理解和调整。但是那就要开发一套UI了。
不然这种的拼接，代码量很难少掉。


#### run_primary

支持的方法：
1. xpath（采用get获取html代码）
2. post接口调用




### zhihu

目前主要爬取zhihu主页推荐的内容。

知乎推荐板块的内容分类：
1. 回答  `spanName=AnswerPage, subAppName=main`
2. 文章(与是否专栏无关) `spanName=Post, subAppName=column`

行啊，翻了好久推荐，才发现，几个星期时间，过了个年回来，知乎就不推荐视频了，把视频单独放一栏了。那刚好给我省事了。



### clients

此模块实现了两套爬虫基础客户端，主要是为了方便用户能够基于自己的习惯采用不同的库，也可以两个库混合使用。

#### requests_client

此类主要是实现纯粹的基于Requests库的一个爬虫基础类，包含了一个session的创建与初始化，
并实现了一个默认的登录方法，如果登录方法需要定制，则可以对Client.login方法进行重写。

## References

[动态渲染页面](https://blog.csdn.net/qq_72290695/article/details/131414557#:~:text=html%20%3D%20response.html.html%201%20from%20requests_html%20import%20HTMLSession,%E6%B8%B2%E6%9F%93%E9%A1%B5%E9%9D%A2%207%20response.html.render%20%28%29%208%20%23%20%E8%8E%B7%E5%8F%96%E9%A1%B5%E9%9D%A2%E6%BA%90%E7%A0%81%20%E6%9B%B4%E5%A4%9A%E9%A1%B9%E7%9B%AE)

[利用字符串获取类名进行实例化 1](https://segmentfault.com/q/1010000012379189) [2](https://segmentfault.com/q/1010000012792068) [3](https://www.runoob.com/w3cnote/python-locals-globals.html#:~:text=locals%20%E6%98%AF%E5%8F%AA%E8%AF%BB%E7%9A%84%EF%BC%8Cglobals%20%E4%B8%8D%E6%98%AF%E3%80%82%20locals%20%E4%B8%8D%E5%8F%AF%E4%BF%AE%E6%94%B9%EF%BC%8Cglobals%20%E5%8F%AF%E4%BB%A5%E4%BF%AE%E6%94%B9%EF%BC%8C%E5%8E%9F%E5%9B%A0%E6%98%AF%EF%BC%9A%20locals,%28%29%20%E5%AE%9E%E9%99%85%E4%B8%8A%E6%B2%A1%E6%9C%89%E8%BF%94%E5%9B%9E%E5%B1%80%E9%83%A8%E5%90%8D%E5%AD%97%E7%A9%BA%E9%97%B4%EF%BC%8C%E5%AE%83%E8%BF%94%E5%9B%9E%E7%9A%84%E6%98%AF%E4%B8%80%E4%B8%AA%E6%8B%B7%E8%B4%9D%E3%80%82%20%E6%89%80%E4%BB%A5%E5%AF%B9%E5%AE%83%E8%BF%9B%E8%A1%8C%E4%BF%AE%E6%94%B9%EF%BC%8C%E4%BF%AE%E6%94%B9%E7%9A%84%E6%98%AF%E6%8B%B7%E8%B4%9D%EF%BC%8C%E8%80%8C%E5%AF%B9%E5%AE%9E%E9%99%85%E7%9A%84%E5%B1%80%E9%83%A8%E5%90%8D%E5%AD%97%E7%A9%BA%E9%97%B4%E4%B8%AD%E7%9A%84%E5%8F%98%E9%87%8F%E5%80%BC%E5%B9%B6%E6%97%A0%E5%BD%B1%E5%93%8D%E3%80%82%20globals%20%28%29%20%E8%BF%94%E5%9B%9E%E7%9A%84%E6%98%AF%E5%AE%9E%E9%99%85%E7%9A%84%E5%85%A8%E5%B1%80%E5%90%8D%E5%AD%97%E7%A9%BA%E9%97%B4%EF%BC%8C%E8%80%8C%E4%B8%8D%E6%98%AF%E4%B8%80%E4%B8%AA%E6%8B%B7%E8%B4%9D%E4%B8%8E%20locals%20%E7%9A%84%E8%A1%8C%E4%B8%BA%E5%AE%8C%E5%85%A8%E7%9B%B8%E5%8F%8D%E3%80%82) [4](https://zky.name/article/72.html#:~:text=__import,b%E5%B0%86%E5%AF%BC%E5%85%A5b%E6%A8%A1%E5%9D%97%E3%80%82) [5]()

[__import__内置方法的fromlist参数，巨坑！](https://zky.name/article/72.html#:~:text=__import,b%E5%B0%86%E5%AF%BC%E5%85%A5b%E6%A8%A1%E5%9D%97%E3%80%82)

[发现了一个很牛的爬虫库的样子，本项目估计是不会去学这个的，到时再研究研究](https://www.jianshu.com/p/72a1f57b333a)

[如何在python项目中添加js的依赖（和前端直接加一样，只是注意下目录就好了）](https://www.cnblogs.com/presleyren/p/11751050.html#:~:text=%E4%B8%80.%E5%AE%89%E8%A3%85%E4%BE%9D%E8%B5%96%20npm%20install%20jsdom%20%E4%BA%8C.%E5%AF%BC%E5%85%A5%E5%8C%85%20js_obj%20%3D%20execjs.,%3D%20dom.window%3B%20document%20%3D%20window.document%3B%20XMLHttpRequest%20%3D%20window.XMLHttpRequest%3B)

