import json, urllib.request, urllib.error
url='http://127.0.0.1:9009/kernel/demo/shell/event'
points = [(70,218),(240,253),(18,568),(240,500)]
for (x,y) in points:
    data=json.dumps({'x':x,'y':y}).encode('utf-8')
    req=urllib.request.Request(url,data,{'Content-Type':'application/json'})
    try:
        resp=urllib.request.urlopen(req,timeout=5)
        body = resp.read().decode('utf-8')
        print('==',x,y,'==')
        try:
            print(json.dumps(json.loads(body), indent=2))
        except Exception:
            print(body)
    except urllib.error.HTTPError as e:
        print('HTTPError', x, y, e.code)
        try:
            err = e.read().decode('utf-8')
            print(err)
        except Exception as ex:
            print('Could not read error body:', ex)
    except Exception as e:
        print('ERR',x,y,str(e))
