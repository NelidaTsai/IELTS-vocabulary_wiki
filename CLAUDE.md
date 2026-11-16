# CLAUDE.md — IELTS 單字知識庫（LLM Wiki）

> 這份文件是給 AI（Claude Code、Codex、Cursor 等）讀的專案規則，也就是 LLM Wiki 的 **schema**。
> **動手修改任何檔案、或回答任何單字問題之前，請先讀完這份文件。** 規則與使用者當下的指示衝突時，以使用者指示為準，並在回覆中說明你偏離了哪一條。

---

## 1. 專案目的

Nelida 準備雅思（IELTS）用的單字知識庫。

- **問題**：單字背了就忘，筆記散在各處；同一個主題的字、意思相近的字之間沒有串起來，寫作時想不到能用哪些字。
- **做法**：採用 Andrej Karpathy 的 **LLM Wiki** 模式（第 2 節）。Nelida 只負責把單字筆記放進 `raw/vocab/`，AI 負責把它整理成一字一頁、互相連結的 Markdown 知識庫，並依主題與學習方法串起來。
- **網站**：把知識庫呈現在 GitHub Pages 上，可以依主題篩選、搜尋單字、瀏覽問答紀錄。
- **長期目標**：每背一批新字，只要新增一個 raw 筆記檔並執行 `/ingest`，知識庫和網站就會自動長大；問 AI 單字問題時，它只根據這個知識庫回答。
- **不做的事**：不放整本單字書、不複製版權教材的內容、不接後端或資料庫系統。

## 2. 三層架構與三個操作（LLM Wiki）

```
raw/vocab/*.md        ──ingest──▶    wiki/                  ──build──▶   網站
單字筆記（人放入）                    知識庫（AI 維護）                     index.html、wiki.html
                                     words/ topics/ concepts/ queries/
```

| 層 | 位置 | 誰負責 | 規則 |
|---|---|---|---|
| **raw** 原始資料 | `raw/vocab/` | Nelida 放入 | **AI 只讀，不修改、不刪除。** 這是知識庫唯一的事實來源。要更正就新增一個筆記檔。 |
| **wiki** 知識庫 | `wiki/` | AI 撰寫與維護 | Markdown，頁面之間用相對連結互連，每頁標註 `sources`。 |
| **schema** 規則 | `CLAUDE.md` | Nelida 與 AI 討論後修改 | 就是本文件。 |
| **網站** 呈現 | `index.html`、`wiki.html` | 由腳本從 wiki 產生資料 | 網站不另外存資料，全部讀 `assets/js/wiki-data.js`。 |

**三個操作**（步驟見第 8 節）：

- **ingest**：`raw/vocab/` 有新筆記 → 建立單字頁 → 更新主題頁、學習方法頁 → 更新 `wiki/index.md` → 在 `wiki/log.md` 記一筆。
- **query**：回答單字問題，**只能根據 wiki 的內容**，並附上引用頁面（第 3 節）。
- **lint**：檢查知識庫健康度：漏掉沒 ingest 的字、斷掉的連結、孤兒頁、缺來源、頁面之間互相矛盾。

**兩個特殊檔**：

- `wiki/index.md`：**內容目錄**。依類型列出每一頁＋一句摘要。query 與 ingest 前都要先讀它。
- `wiki/log.md`：**操作紀錄**。依時間由舊到新、只往後加。標題固定為 `## [YYYY-MM-DD] ingest|query|lint | 對象`，可用 `grep "^## \[" wiki/log.md | tail -5` 看最近 5 筆。

## 3. 最重要的規則：只能用知識庫回答

使用者問任何單字相關問題（意思、用法、同義字、某主題能用哪些字、例句……）時：

1. **先讀 `wiki/index.md`**，找出相關頁面，再讀那些頁面。
2. **只使用 wiki 裡寫的內容回答。** 不可以用自己原本知道的英文知識補充，即使你很確定。
3. **每個回答都要附上「引用」**：列出用到的 wiki 頁面（相對連結或路徑）。
4. **知識庫沒有的內容，直接說「知識庫裡沒有」**，並建議：「請把這個字的筆記加進 `raw/vocab/`，再執行 `/ingest`。」不要猜、不要先給答案再補一句「建議確認」。
5. 只有部分資訊時，回答有的部分，並明確指出缺了什麼（例如：「知識庫沒有 decrease 的單字頁，無法確認用法」）。
6. 答案有保存價值（跨單字比較、主題整理、使用者說要存）時，存成 `wiki/queries/<slug>.md`，更新 index 與 log。

範例見 `wiki/queries/not-in-wiki-procrastinate.md`（沒有時怎麼回答）與 `wiki/queries/paraphrase-reduce.md`（只有部分資訊時怎麼回答）。

## 4. 技術限制與檔案結構

| 項目 | 規則 |
|---|---|
| 技術 | 純 HTML + CSS + 原生 JavaScript。不用框架、不用 npm。唯一的建置是 `python3 scripts/build_wiki.py`（只用標準函式庫）。 |
| 部署 | GitHub Pages，`main` 分支根目錄。所有路徑用**相對路徑**，禁止以 `/` 開頭。 |
| 本機預覽 | 雙擊 `index.html` 就要能看，所以資料放在 `.js`（`window.WIKI`），**不要用 `fetch()`**。 |
| 外部資源 | 只允許 Google Fonts。不引入其他 CDN（Markdown 由 `wiki.js` 內建的簡易渲染器處理）。 |
| 語言 | 說明文字用繁體中文（台灣用語）；單字、例句、搭配用英文。 |

```
.
├── CLAUDE.md                       ← 本文件（schema）
├── AGENTS.md                       ← 給其他 AI 工具，指向本文件
├── README.md                       ← 給人看的說明
├── index.html                      ← 首頁：統計、主題、單字卡（篩選＋搜尋）、問答紀錄、運作方式
├── wiki.html                       ← 知識庫頁：側欄目錄、搜尋、Markdown 內容、反向連結
├── raw/vocab/                      ← ★ 原始資料：單字筆記（AI 只讀）
│   ├── YYYY-MM-DD-<topic>.md       ← 主題單字筆記（8 欄）
│   └── YYYY-MM-DD-usage.md         ← 用法補充筆記（4 欄）
├── wiki/                           ← ★ 知識庫（AI 維護）
│   ├── index.md / log.md
│   ├── words/<word>.md             ← 單字頁，一字一頁
│   ├── topics/<topic>.md           ← 主題頁（environment、education…）
│   ├── concepts/<name>.md          ← 學習方法頁（搭配詞、同義替換、字族…）
│   └── queries/<slug>.md           ← 問答紀錄
├── assets/
│   ├── css/style.css               ← 全站唯一樣式檔
│   └── js/
│       ├── wiki-data.js            ← 自動產生，勿手改
│       ├── main.js                 ← 首頁渲染
│       └── wiki.js                 ← 知識庫頁渲染
├── scripts/
│   ├── build_wiki.py               ← wiki/*.md → assets/js/wiki-data.js
│   └── check.py                    ← 結構檢查＋wiki lint
└── .claude/commands/               ← /ingest、/ask、/lint
```

不要新增上面沒列出的頂層資料夾或檔案（`check.py` 會擋）。

## 5. raw 筆記格式（`raw/vocab/YYYY-MM-DD-<topic>.md`）

- 檔名：日期＋主題代號，主題代號必須和 `wiki/topics/<topic>.md` 一致，例如 `2026-11-20-health.md`。新主題就用新代號，ingest 時建立主題頁。
- 內容：標題、說明（來源、是否已校對），然後一個 8 欄表格：

```markdown
| word | 詞性 | 中文 | 英文解釋 | 例句 | 常見搭配 | 同義替換 | 字族 |
|---|---|---|---|---|---|---|---|
| mitigate | v. | 減輕、緩和 | to make something harmful less severe | Planting trees can help mitigate ... | mitigate the impact; mitigate risks | alleviate; reduce | mitigation (n.) |
```

- 同一格有多個項目時用 `;` 分隔；沒有的欄位填 `—`。
- 使用者給的筆記不是這個格式（例如一段文字、照片、隨手清單）時，**另存一份照原樣的檔案**，ingest 時再整理；不要改寫使用者的原檔。
- 例句與解釋要自己寫或來自 Nelida 的筆記，不要整段複製版權教材。

**用法補充筆記** `raw/vocab/YYYY-MM-DD-usage.md`：為已有的字補充不同用法（詞性變化、固定句型、不同語意）。檔名以 `-usage` 結尾，不對應主題。格式為 4 欄表格，一列一種用法：

```markdown
| word | 用法 | 例句 | 說明 |
|---|---|---|---|
| mitigate | 被動語態 | The risks can be mitigated through careful planning. | 寫作中常用被動，語氣較客觀 |
```

- 同一個字通常寫 2～4 列，用法之間要真的不同（不同句型、詞性或語意），不要只是換個主詞。
- 表中的字必須已經有單字頁；新字請先寫進主題筆記。

## 6. wiki 頁面格式

每頁以 frontmatter 開頭（`key: value`，一行一個），正文**不寫 H1**，從 `##` 開始。各類型的欄位與**必備區塊（順序固定）**：

### 6.1 單字頁 `wiki/words/<word>.md`

```markdown
---
title: mitigate                ← 與檔名相同，全小寫
type: word
summary: v. 減輕、緩和          ← 詞性＋中文，首頁卡片與目錄使用
pos: v.                        ← n. / v. / adj. / adv. / prep. / conj. / phr.
zh: 減輕、緩和
topic: environment             ← 對應 wiki/topics/<topic>.md
sources: raw/vocab/2026-11-16-environment.md
updated: 2026-11-16
---
```

必備區塊：`意思`（**詞性** 中文：英文解釋）、`例句`（用 `>` 引用）、`不同用法`、`常見搭配`、`同義替換`、`字族`、`相關單字`（2 個以內，連到其他單字頁並註明詞性與中文）、`主題`（連到主題頁）。搭配、同義替換、字族三個區塊最後一行連到對應的學習方法頁。

`不同用法` 區塊的寫法（來自用法補充筆記，**至少 2 種**）：

```markdown
## 不同用法

### 1. 被動語態

> The risks can be mitigated through careful planning.

寫作中常用被動，語氣較客觀。
```

每種用法一個 `### 編號. 用法名稱`，下面是 `>` 例句與一句中文說明。還沒有用法補充筆記的字，寫 `> 待補：尚無用法補充筆記` 並在 log 記錄。

### 6.2 主題頁 `wiki/topics/<topic>.md`

frontmatter：`title`（`English 中文`，例如 `Environment 環境`）、`type: topic`、`summary`、`sources`、`updated`。
必備區塊：`單字一覽`（表格：單字連結／詞性／中文，**必須列出該主題所有單字**）、`依用途分組`（例如描述問題／提出解決方式）、`例句精選`（從單字頁挑 2 句）、`相關`。

### 6.3 學習方法頁 `wiki/concepts/<name>.md`

frontmatter：`title`、`type: concept`、`summary`、`sources`、`updated`。
必備區塊：`定義`、`知識庫中的例子`（表格，例子只能來自已有的單字頁並加連結）；可再加 `注意`、`相關`。

### 6.4 問答頁 `wiki/queries/<slug>.md`

frontmatter：`title`（問題本身）、`type: query`、`summary`、`asked`（提問日期）、`updated`。
必備區塊：`問題`、`回答`（只用 wiki 內容，提到的字都加連結）、`引用`（列出所有用到的 wiki 頁面；**不可引用外部網址**）。

### 6.5 連結規則

- 用相對路徑的 Markdown 連結，例如在單字頁裡寫 `[conservation](conservation.md)`、`[搭配詞](../concepts/collocation.md)`。在 GitHub 上和網站上都能點。
- 每個單字、主題、學習方法頁至少被 **2 個地方**連結（含 index），否則 lint 會提醒。
- 一個學習技巧或概念在 3 個以上單字頁都用得到時，就新增學習方法頁。
- 不同筆記對同一個字說法不同時，在單字頁寫明「筆記 A：…；筆記 B：…」，並記在 log，不要自己挑一個。

## 7. 視覺風格

方向：**「紙本單字本」**，溫暖米白底、深墨色文字、單一靛藍強調色，大量留白。

- **固定使用明亮的淺色主題**（不跟隨系統深色模式）。背景接近白色、文字深墨色、強調色為明亮的藍色。
- **顏色只能用 `style.css` 最上方 `:root` 的 CSS 變數**（`--paper`、`--paper-2`、`--ink`、`--ink-2`、`--line`、`--accent`、`--accent-soft`、`--warn`、`--warn-soft`），不可寫死色碼。
- **字體**：標題與英文單字用 `--font-serif`；內文 `--font-sans`；詞性、統計標籤、路徑用 `--font-mono`。
- **元件**：卡片圓角 `--radius`、細線框、淡陰影；單字卡上英文單字用強調色；單字頁的例句以淡藍底色區塊呈現。不用漸層按鈕、不用 emoji 當圖示。
- **RWD**：≤ 720px 時主題卡單欄、單字卡雙欄、知識庫側欄變成標籤式按鈕。
- 不寫 inline style、不在 HTML 加 `<style>`；新元件寫在 `style.css` 對應區段。

## 8. 標準工作流程

### 8.1 ingest：整理新筆記（`/ingest`）

1. 讀 `wiki/index.md`，確認目前有哪些單字、主題、學習方法頁。
2. 讀新的 `raw/vocab/` 筆記（只讀）。用 2～3 句告訴使用者這批字的重點；若有字已經存在，指出來。
3. 每個新字建立 `wiki/words/<word>.md`（6.1）。用法補充筆記則把每列寫進對應單字頁的「不同用法」區塊。已存在的字：把新資訊合併進去、`sources` 加上新筆記、更新 `updated`；說法衝突照 6.5 處理。
4. 為新字找 1～2 個「相關單字」（同主題或可搭配使用），並在對方頁面也加上反向連結。
5. 更新或建立主題頁（6.2），確保單字一覽完整。
6. 在學習方法頁補充有代表性的新例子；需要時新增學習方法頁。
7. 更新 `wiki/index.md`（單字表依字母排序）。
8. 在 `wiki/log.md` 最下面加 `## [日期] ingest | 主題`：來源、新增／更新的頁面、衝突與備註。
9. 執行 `python3 scripts/build_wiki.py`，再執行 `python3 scripts/check.py`，必須「全部通過」。

### 8.2 query：回答問題（`/ask`）

依第 3 節。回答完問使用者要不要存成問答頁；存了就更新 index、記 log（`## [日期] query | 問題`）、重新 build 與 check。

### 8.3 lint：健康檢查（`/lint`）

1. 執行 `python3 scripts/check.py`，修正所有錯誤，處理提醒。
2. 人工檢查腳本抓不到的：例句是否真的用到該字、中文解釋與詞性是否一致、相關單字是否合理、問答頁的回答是否超出知識庫內容。
3. 記 log：`## [日期] lint | 範圍`。

### 8.4 修改網站

- 先說明要改什麼、為什麼。改了共用樣式，要確認首頁與知識庫頁都正常（含手機寬度）。
- 新增頁面類型、欄位或區塊時，**同步更新本文件、`check.py`、`wiki.js` 的 `TYPE_LABELS`／`GROUPS`**。

## 9. AI 必須遵守的規則（總整理）

1. **只能用知識庫回答單字問題**，並附引用；沒有就說沒有（第 3 節）。
2. **raw 只讀**，不修改、不刪除 `raw/` 的任何檔案。
3. **不編造**：wiki 裡的意思、例句、搭配、同義字只能來自 raw 筆記。`check.py` 會擋「raw 裡沒有的單字頁」。
4. **資料只寫一份**：知識只在 `wiki/`；網站資料 `wiki-data.js` 只能由腳本產生。
5. **每次動到 wiki 都要記 log**，只往後加。
6. **小步修改**：只做被要求的事，其他建議列在回覆裡。
7. **不要改動** `CLAUDE.md`、`AGENTS.md`、`scripts/` 的規則，除非使用者要求或符合 8.4。
8. **完成前一定要跑** `build_wiki.py` 與 `check.py`，修到「全部通過」，不要回報「應該可以」。
9. **不引入新依賴**（框架、套件、CDN）。
10. **Commit 訊息**用中文、動詞開頭，例如 `ingest：Health 健康 6 個字`、`新增問答：環境題用字`。

## 10. 完成定義（Definition of Done）

一次 ingest 要符合以下全部條件才算完成：

- [ ] raw 筆記裡的每個字都有單字頁，八個必備區塊齊全，「不同用法」至少 2 種
- [ ] 主題頁的單字一覽完整，新字至少有 1 個相關單字
- [ ] `wiki/index.md` 與 `wiki/log.md` 已更新
- [ ] `python3 scripts/build_wiki.py` 已執行，`python3 scripts/check.py` 顯示「全部通過」
- [ ] 首頁單字數與主題卡正確，新字可以搜尋到，點進去能開啟知識庫頁
