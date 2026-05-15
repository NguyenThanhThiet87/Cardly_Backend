import requests

url = "https://YOUR_SPACE.hf.space/extract"

files = {"file": open("src\scans\sample\z7824079858417_740fea717b08bd4d56b7943352ebfa15.jpg", "rb")}

res = requests.post(url, files=files)

print("STATUS:", res.status_code)
print("TEXT:", res.text)   # << quan trọng

# chỉ parse json nếu OK
if res.headers.get("content-type", "").startswith("application/json"):
    print(res.json())