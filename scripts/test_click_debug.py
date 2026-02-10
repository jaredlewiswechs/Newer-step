import json, urllib.request
url='http://127.0.0.1:9009/kernel/demo/shell/event'
for (x,y) in [(70,218),(240,253),(18,568)]:
    data=json.dumps({'x':x,'y':y}).encode('utf-8')
    req=urllib.request.Request(url,data,{'Content-Type':'application/json'})
    try:
        resp=urllib.request.urlopen(req,timeout=5)
        print('==',x,y,'==')
        print(resp.read().decode())
    except Exception as e:
        print('ERR',x,y,e)
