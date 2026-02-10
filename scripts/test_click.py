import json
import urllib.request

url='http://127.0.0.1:9009/kernel/demo/shell/event'
data=json.dumps({'x':240,'y':253}).encode('utf-8')
req=urllib.request.Request(url,data,{'Content-Type':'application/json'})
resp=urllib.request.urlopen(req,timeout=5)
print(resp.status)
print(resp.read().decode())
