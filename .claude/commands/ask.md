---
description: 只根據知識庫回答單字問題（LLM Wiki 的 query 操作）
argument-hint: 你的問題，例如「教育類題目可以用哪些字？」
---

問題：$ARGUMENTS

**嚴格依照 `CLAUDE.md` 第 3 節回答：**

1. 先讀 `wiki/index.md`，找出相關頁面並讀完。
2. **只使用 wiki 裡寫的內容回答**，不要用你自己原本的英文知識補充。
3. 回答最後附上「引用」，列出用到的 wiki 頁面路徑。
4. 知識庫沒有的內容，直接回答「知識庫裡沒有」，並建議把筆記加進 `raw/vocab/` 後執行 `/ingest`。只有部分資訊時，明確說出缺了什麼。
5. 回答完問我要不要存成 `wiki/queries/` 問答頁；要存的話照第 6.4 節格式建立，更新 index、log，再執行 `build_wiki.py` 與 `check.py`。
