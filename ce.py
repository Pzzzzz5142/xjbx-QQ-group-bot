import requests
import os.path as path
import base64
from PIL import Image
from io import BytesIO


url = r"https://api.lolicon.app/setu/"

data = {
    "db": "999",
    "output_type": "2",
    "numres": "3",
    "url": r"https://gchat.qpic.cn/gchatpic_new/545870222/2088029700-2259245513-681ADB6C48777E0EF7B36AC847BB9673/0?term=2",
}

datas = {"apikey": "367219975ea6fec3027d38", "r18": "1", "size1200": True}


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
}


def request_download(x):
    import requests

    r = requests.get(x)
    with open("img2.png", "wb") as f:
        f.write(r.content)


sessiom = requests.Session()
re = sessiom.get(url, headers=headers, params=datas)
a = re.json()
print("ok" + a["data"][0]["url"])
request_download("https://i.pixiv.cat/img-original/img/2013/07/27/01/10/07/37340439_p0.jpg")
pass
