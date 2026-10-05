from pathlib import Path

from pypdf import PdfReader

HERE = Path(__file__).parent
reader = PdfReader(HERE / "samples" / "报销制度.pdf")

# 覆盖点：
# ① 读 samples/报销制度.pdf → 页数
# ② 逐页 extract_text() 拼整篇 → 打印：页数 / 总字数 / 前 200 字
# ③ 读 data/报销制度.md 源文 → 对比：字数差多少？找出 2-3 处「变形」
#    （重点看：表格、编号、字距、换行 —— 它们变成了什么样，就是要讲回的内容）

text = ""
page_num = len(reader.pages)
for i in range(page_num):
    text += reader.pages[i].extract_text()

print(f"页数：{page_num} 总字数{len(text)}\n{text[:200]}")
