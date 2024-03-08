# 开发日志

## 20240221

纯粹requests的弊端显现了，不是不能用，但是如果不做渲染，则需要分析和寻找信息在哪里，然后导致分析太长时间，尤其是像知乎的问题详情居然在init_html里
就直接带上了，万幸是它直接放在了最底下，运气好恰巧找到。

之后还是转为selenium好了，最重要的是快，好的架构先到此为止了，把绝大部分的精力先预留给算法部分。

## 20240225

完成对zse-96加密函数的js功能验证。需要通过`node <filename>`来进行代码debug，以及使js中的proxy函数有效果。

## 20240304

zse-96的加密还是有问题，应该是环境检测还是不对，实在是太折腾了，还是直接用简单的方法v4的api好了。原硬核分析加密复现失败了。

## 20240306 

[这里](https://yifei.me/note/460)虽然有提到评论的获取方式，但是并没有关于子评论的内容，也没有提到root_comment这个接口。

对于一个问题的评论列表的结果，返回内容和answer是一样的，访问示例：
https://www.zhihu.com/api/v4/comment_v5/questions/571869970/root_comment?order_by=score&limit=20&offset=

对于文章的也是：
https://www.zhihu.com/api/v4/comment_v5/articles/679884390/root_comment?order_by=score&limit=20&offset=

想法的话，还涉及转发，先不搞了。

## 20240307

文章，问题，回答，三个可能性来讲，推荐只会给出文章和回答的两种。

这里记录下两种类型在run_primary之后得到的格式。

https://www.zhihu.com/question/511958588/answer/3351435291

https://zhuanlan.zhihu.com/p/678130904

https://zhuanlan.zhihu.com/p/553672804

https://www.zhihu.com/api/v4/{target_type}s/{answer_id}/root_comments?limit=20&offset=&order_by=normal, 这个的comments要有s，而comment_v5不用。
limit最大20.
