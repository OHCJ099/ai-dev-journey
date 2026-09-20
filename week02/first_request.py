import httpx

request = httpx.get("https://httpbin.org/get")

status_code = request.status_code
resp = request.json()

if status_code != 200:
    print(f"错误！状态码: {status_code}")
else:
    print(f"状态码: {status_code} URL: {resp['url']}")