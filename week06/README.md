# FastAPI路由 · 继承类，装饰器与错误码

运行：`uv add fastapi uvicorn`

`uv run uvicorn week06.main:app --reload`

安装FastAPI虚拟环境并运行路由服务，然后拉起持久化服务，才能调用接口传入message参数就可以获得模型响应，有上游供应商和下游接口调用方错误兜底机制。

`/chat` 的接口契约

-  "/chat" 入参：

  ```
  (
  	message: str,
  	system: str = "你是一个有帮助的助手",
  	temperature: float = Field(default=1.0, ge=0.0, le=2.0, 
  )
  ```

- "/chat" 出参

  ```
  -> dict[str, str]
  ```

- 错误码表

  ```
  请求体不合契约（新增）
  触发条件：缺 message、字段类型错、temperature 越界（不在 0~2）
  返回状态码：422
  返回信息：FastAPI/Pydantic 自动生成，形如 {"detail": [...]}
  调用方该做什么：改请求体，别重试；照 detail 里的字段名修
  
  AuthenticationError
  触发条件：上游 API Key 无效或失效
  返回状态码：500
  返回信息：上游Key失效, 请联系管理员
  调用方该做什么：别重试，找服务端管理员
  
  APITimeoutError
  触发条件：请求上游超时
  返回状态码：503
  返回信息：请求超时, 请稍后
  调用方该做什么：可稍后重试，建议退避
  
  APIConnectionError
  触发条件：无法连接上游服务
  返回状态码：503
  返回信息：API连接失败
  调用方该做什么：可稍后重试，建议退避
  
  APIStatusError（e.status_code == 402）
  触发条件：上游返回 402，余额不足
  返回状态码：503
  返回信息：上游余额不足, 请联系管理员
  调用方该做什么：别重试，找服务端管理员充值
  
  APIStatusError（e.status_code == 429）
  触发条件：上游返回 429，请求过于频繁
  返回状态码：503
  返回信息：请求太频繁，请重试
  调用方该做什么：退避后再重试，别立刻猛冲
  
  APIStatusError（其他状态码）
  触发条件：上游返回其他未预期状态码
  返回状态码：500
  返回信息：上游未知错误, 请联系管理员
  调用方该做什么：别重试，上报服务端排查
  
  上游 200 但内容为空（新增）
  触发条件：resp 成功，但 resp.choices[0].message.content 为空
  返回状态码：502
  返回信息：上游收到无效响应
  调用方该做什么：可重试一两次；仍失败则上报服务端
  
  对外状态码汇总
  
  422：请求体不合契约（框架自动）
  500：AuthenticationError、APIStatusError（其他状态码）
  502：上游 200 但内容为空
  503：APITimeoutError、APIConnectionError、APIStatusError(402)、APIStatusError(429)
  ```

踩的坑：

1. 现象：resp = client.chat.completions.create()传入参数错误，客户端处直接报错500 Internal Server Error
   原因：根本原因是对resp = client.chat.completions.create()的传入参数不熟悉
   修法：必须按照
   messages=[

   ​        {"role": "system", "content": <提示词>},

   ​        {"role": "user", "content": <消息>},

   ​	]

   来正确传参

2. 现象：resp = client.chat.completions.create()错填了stream=True导致开启流式传输，导致拿不到content必然报错
   原因：根本原因是也对resp = client.chat.completions.create()的传入参数不熟悉, 流式传输返回的不是完整的响应的content，直接.choices[0].message.content会报错
   修法：将取值调整False

3. 现象：把全仓（含 `handbook/07`）都格式化了
   原因：`ruff format .` 会把全仓都格式化包括README.md或其他没有格式化需求的内容
   修法：添加具体文件路径例如 uvx ruff format ./week06/main.py