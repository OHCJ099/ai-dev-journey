"""W14 离线调试入口：假向量只验证接口与入库数据流，不证明语义质量。

运行 uvicorn api_lab:app；正式 api.py 不负责设置假向量。
"""

from types import SimpleNamespace

import api
import config
import qa
from demo_w13 import enable_offline

api.INDEX_PATH = config.OFFLINE_INDEX_PATH


def fake_create(**kwargs):
    """明确标记的聊天替身：只核对请求接线，不生成真实答案。"""
    messages = kwargs["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "参考材料：" in messages[1]["content"]
    assert "问题：" in messages[1]["content"]

    message = SimpleNamespace(
        content="【离线测试占位，非模型答案】回答生成接线已执行。"
    )

    # 👇 关键：补上 usage 字段，骗过读取 token 用量的代码
    usage = SimpleNamespace(prompt_tokens=10, completion_tokens=20, total_tokens=30)

    return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=usage)


enable_offline()
qa.client = SimpleNamespace(
    chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
)
app = api.app
