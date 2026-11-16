---
description: 把 raw/vocab/ 的新單字筆記整理進 wiki 知識庫
argument-hint: 筆記檔名，例如 raw/vocab/2026-11-20-health.md（可直接貼上單字清單）
---

請對以下單字筆記執行 ingest：

$ARGUMENTS

**嚴格依照 `CLAUDE.md` 第 8.1 節**：

1. 讀 `CLAUDE.md` 第 2、5、6 節與 `wiki/index.md`。
2. 如果我貼的是文字而不是檔案，先照第 5 節存成 `raw/vocab/YYYY-MM-DD-<topic>.md`（缺的欄位填「—」，不要自己補意思或例句）。
3. 讀筆記（**只讀，不修改 raw**），用 2～3 句告訴我這批字的重點，指出已經存在的字。
4. 建立或更新單字頁（七個必備區塊）、相關單字的雙向連結、主題頁、學習方法頁的例子。
5. 更新 `wiki/index.md`；在 `wiki/log.md` 最下面加 `## [今天日期] ingest | 主題`。
6. 執行 `python3 scripts/build_wiki.py` 與 `python3 scripts/check.py`，修到「全部通過」。
7. 回覆：新增／更新的頁面、衝突與待確認事項。
