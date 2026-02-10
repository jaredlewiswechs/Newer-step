import requests

base = "http://127.0.0.1:9009"
print("launching window...")
r = requests.post(base + "/kernel/demo/shell/launch", json={"title": "TestWindow"})
print("launch resp:", r.json())
print("list:", requests.get(base + "/kernel/demo/shell/list").json())
svg = requests.get(base + "/kernel/demo/shell").text
print("svg contains window title:", "TestWindow" in svg)
print("sending click at 100,100")
r = requests.post(base + "/kernel/demo/shell/event", json={"x": 100, "y": 100})
print("click response:", r.json())
print("status page code:", requests.get(base + "/kernel/demo/shell_page").status_code)
