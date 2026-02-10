from Kernel.demo import server

app = server.app
print("Routes:")
for r in app.routes:
    print(r.path, r.methods)
