import execjs

with open('zhihu_comments.js', encoding='utf-8') as f:
    js_code = f.read()
ctx = execjs.compile(js_code)

# 第一个参数为ja代码中的函数名, 后面为函数对应的参数
result = ctx.eval("fff(1514).ZP('AKCWoCX1aRaPTtF701AKJHpXNpYb5j__8iQ=|1677847816')")
pass
