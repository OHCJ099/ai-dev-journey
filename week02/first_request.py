import httpx

resp = httpx.get("https://httpbin.org/get")

status_code = resp.status_code
data = resp.json()

if status_code != 200:
    print(f"错误！状态码: {status_code}")
else:
    print(f"状态码: {status_code} URL: {data['url']}")