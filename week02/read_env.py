import os

from dotenv import load_dotenv

load_dotenv()            # ① 把 .env 读进环境变量
key = os.getenv("DEEPSEEK_API_KEY")
if not key: # ② 从环境变量里取一个值出来
    print("没找到key")
else:
    print(f"发现key: 长度 {len(key)}")