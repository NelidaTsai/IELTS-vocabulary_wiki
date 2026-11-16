---
title: 操作紀錄
type: log
summary: 依時間排列、只往後加的 wiki 操作紀錄（ingest / query / lint）。
updated: 2026-11-16
---

每筆紀錄的標題格式固定為 `## [YYYY-MM-DD] 操作 | 對象`，可以用 `grep "^## \[" wiki/log.md` 快速列出。新紀錄加在最下面。

## [2026-11-16] ingest | Environment 環境

- 來源：`raw/vocab/2026-11-16-environment.md`
- 新增：topics/environment、words/deteriorate、sustainable、emission、mitigate、biodiversity、conservation
- 新增學習方法頁：concepts/collocation、paraphrasing、word-family

## [2026-11-16] ingest | Education 教育

- 來源：`raw/vocab/2026-11-16-education.md`
- 新增：topics/education、words/curriculum、compulsory、literacy、vocational、tuition、cognitive
- 更新：concepts/collocation、paraphrasing、word-family（加入例子）
- 備註：tuition 的字族在筆記中為「—」，單字頁標示「筆記中未列出」。

## [2026-11-16] ingest | Technology 科技

- 來源：`raw/vocab/2026-11-16-technology.md`
- 新增：topics/technology、words/innovation、obsolete、automation、surveillance、ubiquitous、privacy
- 跨主題連結：vocational ↔ automation（技職訓練與自動化對工作的影響）

## [2026-11-16] query | 環境類 Task 2 可以用哪些字？

- 依 topics/environment 與 6 個單字頁回答，存成 queries/environment-task2-words。

## [2026-11-16] query | 想替換 reduce，可以用哪些字？

- 依 words/mitigate、words/emission 回答；decrease、diminish 不在知識庫，未回答。存成 queries/paraphrase-reduce。

## [2026-11-16] query | procrastinate 是什麼意思？

- 知識庫沒有此字，依規則不回答，建議 ingest。存成 queries/not-in-wiki-procrastinate 作為示範。

## [2026-11-16] lint | 全站

- `python3 scripts/check.py`：全部通過。18 個單字都有頁面，raw 筆記中的每個字都已 ingest。
