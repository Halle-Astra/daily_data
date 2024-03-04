import execjs

with open('zse96v2.js', encoding='utf-8') as f:
    js_code = f.read()
ctx = execjs.compile(js_code)

# 第一个参数为ja代码中的函数名, 后面为函数对应的参数
result = ctx.eval("fff(1514).ZP('AKCWoCX1aRaPTtF701AKJHpXNpYb5j__8iQ=|1677847816')")
res = ctx.call("zse96", "https://zhihu.com","hhlajklsdfkNLSKDJF")

v = '101_3_3.0+/api/v4/comment_v5/answers/3378778819/root_comment?order_by=score&limit=20&offset=+AKCWoCX1aRaPTtF701AKJHpXNpYb5j__8iQ=|1677847816'

res = ctx.call('encrypt_core', 'E6705659DBA07517B6AE1C5851F2749B'.lower())
pass
