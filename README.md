# IELTS 單字知識庫（LLM Wiki）

我準備雅思用的單字知識庫。參考 Andrej Karpathy 的 [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)：我只負責把單字筆記放進 `raw/vocab/`，AI 依照 [`CLAUDE.md`](CLAUDE.md) 的規則把它整理成一字一頁、互相連結的知識庫，再呈現成網站。

- 網站：https://nelidatsai.github.io/IELTS-vocabulary_wiki/
- 知識庫頁：https://nelidatsai.github.io/IELTS-vocabulary_wiki/wiki.html
- 規則：[`CLAUDE.md`](CLAUDE.md)（其他 AI 工具看 [`AGENTS.md`](AGENTS.md)）

## 架構

```
raw/vocab/*.md   ──ingest──▶   wiki/   ──build──▶   index.html、wiki.html
單字筆記（只讀）                 知識庫（AI 維護）       網站
```

| 位置 | 內容 |
|---|---|
| `raw/vocab/` | 單字筆記（8 欄表格：單字、詞性、中文、英文解釋、例句、搭配、同義替換、字族），AI 只讀不改 |
| `wiki/words/` | 單字頁，一字一頁 |
| `wiki/topics/` | 主題頁：Environment、Education、Technology |
| `wiki/concepts/` | 學習方法：搭配詞、同義替換、字族 |
| `wiki/queries/` | 問答紀錄：只根據知識庫回答，附引用 |
| `wiki/index.md`、`wiki/log.md` | 目錄與操作紀錄 |

## 規則重點

- **只能用知識庫回答**：問 AI 單字問題時，它只能根據 wiki 回答並附引用；知識庫沒有就說沒有（範例：`wiki/queries/not-in-wiki-procrastinate.md`）。
- **不編造**：wiki 的內容只能來自 raw 筆記，`check.py` 會擋 raw 裡沒有的單字頁。
- **可檢查**：`scripts/check.py` 檢查頁面格式、必備區塊、斷掉的連結、孤兒頁、漏掉沒 ingest 的字、log 格式。

## 新增單字

1. 新增 `raw/vocab/YYYY-MM-DD-<topic>.md`（格式見 CLAUDE.md 第 5 節）
2. 在 Claude Code 執行 `/ingest raw/vocab/YYYY-MM-DD-<topic>.md`
3. 問問題：`/ask 健康類題目可以用哪些字？`

手動檢查：

```
python3 scripts/build_wiki.py   # wiki/*.md → assets/js/wiki-data.js
python3 scripts/check.py        # 必須「全部通過」
```

## 本機預覽與部署

雙擊 `index.html` 即可預覽。部署：Settings → Pages → Deploy from a branch → `main` / `(root)`。

> 初始的 18 個單字由 Claude 整理、例句自行撰寫，待 Nelida 校對。
