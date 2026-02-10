import json, urllib.request, urllib.error
url='http://127.0.0.1:9009/kernel/demo/shell/event'
points=[(70,218),(240,253),(18,568)]
for (x,y) in points:
    data=json.dumps({'x':x,'y':y}).encode('utf-8')
    req=urllib.request.Request(url,data,{'Content-Type':'application/json'})
    try:
        resp=urllib.request.urlopen(req,timeout=5)
        print('==',x,y,'==')
        print(resp.read().decode())
    except urllib.error.HTTPError as e:
        print('ERR HTTP',x,y,e.code)
        try:
            body=e.read().decode()
            print('BODY:\n',body)
        except Exception as ex:
            print('BODY READ ERROR',ex)
    except Exception as e:
        print('ERR',x,y,e)
