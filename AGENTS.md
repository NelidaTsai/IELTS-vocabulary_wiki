# AGENTS.md

本專案的完整規則寫在 **[`CLAUDE.md`](CLAUDE.md)**，所有 AI 工具（Codex、Cursor、Copilot、Gemini 等）都適用同一份規則。**開始任何修改或回答任何單字問題之前，請先完整閱讀 `CLAUDE.md`。**

最重要的幾條（摘要，細節以 `CLAUDE.md` 為準）：

1. **只能用知識庫回答。** 單字問題先讀 `wiki/index.md` 再讀相關頁面，只根據 wiki 內容回答並附引用；沒有就說「知識庫裡沒有」，建議加進 `raw/vocab/` 再 ingest。
2. 採用 Karpathy 的 LLM Wiki 三層架構：`raw/vocab/`（單字筆記，**只讀不改**）→ `wiki/`（AI 維護的知識庫）→ 網站。
3. 三個操作：**ingest**（新筆記 → 單字頁、主題頁、index、log）、**query**（只用 wiki 回答）、**lint**（`python3 scripts/check.py`）。
4. wiki 頁面有固定的 frontmatter 與必備區塊（單字、主題、學習方法、問答四種），單字頁要有至少 2 種「不同用法」，格式見 `CLAUDE.md` 第 5、6 節。
5. 純 HTML／CSS／原生 JS，不用框架、CDN、`fetch()`，全部使用相對路徑；`assets/js/wiki-data.js` 由 `python3 scripts/build_wiki.py` 產生，勿手改。
6. 完成前執行 `python3 scripts/build_wiki.py` 與 `python3 scripts/check.py`，必須「全部通過」。
