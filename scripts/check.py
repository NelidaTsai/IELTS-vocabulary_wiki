#!/usr/bin/env python3
"""
結構檢查＋wiki lint：確認專案符合 CLAUDE.md 的規則。
用法：在專案根目錄執行  python3 scripts/check.py
只使用 Python 標準函式庫，不需要安裝任何套件。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_wiki  # noqa: E402

WIKI = ROOT / "wiki"
RAW_VOCAB = ROOT / "raw/vocab"
CSS_FILE = ROOT / "assets/css/style.css"

# 每種頁面：放哪個資料夾、frontmatter 必填欄位、正文必備的 ## 區塊（依序）
TYPES = {
    "word": ("words", ["title", "summary", "pos", "zh", "topic", "sources", "updated"],
             ["意思", "例句", "不同用法", "常見搭配", "同義替換", "字族", "相關單字", "主題"]),
    "topic": ("topics", ["title", "summary", "sources", "updated"], ["單字一覽", "依用途分組", "例句精選", "相關"]),
    "concept": ("concepts", ["title", "summary", "sources", "updated"], ["定義", "知識庫中的例子"]),
    "query": ("queries", ["title", "summary", "asked", "updated"], ["問題", "回答", "引用"]),
    "index": (None, ["title", "summary", "updated"], []),
    "log": (None, ["title", "summary", "updated"], []),
}
POS = {"n.", "v.", "adj.", "adv.", "prep.", "conj.", "phr."}
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
LOG_HEAD_RE = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})\] (ingest|query|lint) \| .+$")
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")

errors, warnings = [], []
err, warn = errors.append, warnings.append


def raw_words():
    """從 raw/vocab/*.md 的表格讀出所有單字：{word: (topic, 檔案)}"""
    found = {}
    for f in sorted(RAW_VOCAB.glob("*.md")):
        parts = f.stem.split("-", 3)
        topic = parts[3] if len(parts) == 4 else ""
        for line in f.read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if line.startswith("|") and len(cells) >= 8 and cells[0] != "word" and not set(cells[0]) <= set("-: "):
                found[cells[0]] = (topic, f.relative_to(ROOT).as_posix())
    return found


def raw_usages():
    """從 raw/vocab/*-usage.md 的 4 欄表格讀出用法：{word: [(用法, 檔案), ...]}"""
    found = {}
    for f in sorted(RAW_VOCAB.glob("*-usage*.md")):
        for line in f.read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if line.startswith("|") and len(cells) == 4 and cells[0] != "word" and not set(cells[0]) <= set("-: "):
                found.setdefault(cells[0], []).append((cells[1], f.relative_to(ROOT).as_posix()))
    return found


def sections(body):
    return [l[3:].strip() for l in body.splitlines() if l.startswith("## ")]


def check_wiki():
    index_text = (WIKI / "index.md").read_text(encoding="utf-8") if (WIKI / "index.md").exists() else ""
    if not index_text or not (WIKI / "log.md").exists():
        err("wiki/ 必須有 index.md 與 log.md")
    pages, inbound = {}, {}

    for path in sorted(WIKI.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        pid = path.relative_to(WIKI).with_suffix("").as_posix()
        meta, body = build_wiki.parse_page(path)
        pages[pid] = (meta, body, rel)
        ptype = meta.get("type")
        if ptype not in TYPES:
            err(f"{rel}：type「{ptype}」不在允許清單 {sorted(TYPES)}")
            continue
        folder, required, secs = TYPES[ptype]
        for k in required:
            if not meta.get(k):
                err(f"{rel}：frontmatter 缺少 `{k}`")
        if folder and not pid.startswith(folder + "/"):
            err(f"{rel}：type 為 {ptype} 的頁面應放在 wiki/{folder}/")
        if folder and not SLUG_RE.match(path.stem):
            err(f"{rel}：檔名只能用小寫英文、數字、連字號")
        if body.lstrip().startswith("# "):
            err(f"{rel}：正文不要寫 H1，標題由 frontmatter 的 title 提供")
        got = [s for s in sections(body) if s in secs]
        if got != secs:
            err(f"{rel}：必備區塊應依序為 {secs}，目前是 {sections(body)}")
        for src in meta["sources"]:
            if not src.startswith("raw/") or not (ROOT / src).exists():
                err(f"{rel}：來源檔不存在或不在 raw/：{src}")
        if folder and f"]({pid}.md)" not in index_text:
            err(f"{rel}：沒有列在 wiki/index.md")

        if ptype == "word":
            if path.stem != meta.get("title"):
                err(f"{rel}：單字頁檔名應與 title 相同（{meta.get('title')}）")
            if meta.get("pos") not in POS:
                err(f"{rel}：pos「{meta.get('pos')}」不在允許清單 {sorted(POS)}")
            if not (WIKI / "topics" / f"{meta.get('topic')}.md").exists():
                err(f"{rel}：topic「{meta.get('topic')}」沒有對應的 wiki/topics/ 頁")
            elif f"../topics/{meta.get('topic')}.md" not in body:
                err(f"{rel}：「主題」區塊要連到 ../topics/{meta.get('topic')}.md")

        if ptype == "word":
            usage = body.split("## 不同用法", 1)[-1].split("\n## ", 1)[0]
            n_usage = len(re.findall(r"^### \d+\. ", usage, re.M))
            if n_usage < 2 and "待補" not in usage:
                err(f"{rel}：「不同用法」至少要有 2 種（### 1. …），或標示待補")
            if n_usage and usage.count("\n> ") < n_usage:
                err(f"{rel}：「不同用法」每種用法都要有一句 > 例句")

        if ptype == "query":
            cite = body.split("## 引用", 1)[-1]
            if not LINK_RE.search(cite):
                err(f"{rel}：「引用」區塊至少要有一個知識庫頁面連結（只能根據知識庫回答）")
            if re.search(r"\]\(https?:", body):
                err(f"{rel}：問答頁不可引用外部網址，只能引用知識庫頁面")

        for href in LINK_RE.findall(body):
            if re.match(r"^(https?:|mailto:|#)", href):
                continue
            target = (path.parent / href).resolve()
            if not target.exists():
                err(f"{rel}：斷掉的連結 {href}")
            elif target.suffix == ".md" and WIKI in target.parents:
                tid = target.relative_to(WIKI).with_suffix("").as_posix()
                if tid != pid:
                    inbound[tid] = inbound.get(tid, 0) + 1

    # 孤兒頁
    for pid, (meta, _, rel) in pages.items():
        if meta.get("type") in ("word", "topic", "concept") and inbound.get(pid, 0) < 2:
            warn(f"{rel} 只被 {inbound.get(pid, 0)} 個地方連結（含 index），考慮在相關頁面加上連結")

    # ingest 完整性：raw 筆記裡的每個字都要有單字頁，主題頁要列出該主題所有字
    rw = raw_words()
    for word, (topic, src) in rw.items():
        pid = f"words/{word}"
        if pid not in pages:
            err(f"{src} 裡的「{word}」還沒有單字頁（請執行 ingest）")
            continue
        meta, _, rel = pages[pid]
        if src not in meta["sources"]:
            err(f"{rel}：sources 應包含 {src}")
        tpage = pages.get(f"topics/{meta.get('topic')}")
        if tpage and f"../words/{word}.md" not in tpage[1]:
            err(f"wiki/topics/{meta.get('topic')}.md 的單字一覽缺少 {word}")
    for pid, (meta, _, rel) in pages.items():
        if meta.get("type") == "word" and meta.get("title") not in rw:
            err(f"{rel}：raw/vocab/ 的筆記裡找不到這個字（wiki 內容必須來自 raw）")

    # 用法補充筆記：表中的字要有單字頁，且單字頁要引用該筆記、收錄每一種用法
    for word, items in raw_usages().items():
        page = pages.get(f"words/{word}")
        if not page:
            err(f"{items[0][1]} 裡的「{word}」沒有單字頁（請先寫進主題筆記並 ingest）")
            continue
        meta, body, rel = page
        for usage, src in items:
            if src not in meta["sources"]:
                err(f"{rel}：sources 應包含 {src}")
            if usage not in body:
                err(f"{rel}：「不同用法」缺少 {src} 裡的用法「{usage}」")

    # log 格式
    if (WIKI / "log.md").exists():
        heads = [l for l in (WIKI / "log.md").read_text(encoding="utf-8").splitlines() if l.startswith("## ")]
        for h in heads:
            if not LOG_HEAD_RE.match(h):
                err(f"wiki/log.md：標題格式應為「## [YYYY-MM-DD] ingest|query|lint | 對象」：{h}")
        dates = [LOG_HEAD_RE.match(h).group(1) for h in heads if LOG_HEAD_RE.match(h)]
        if dates != sorted(dates):
            err("wiki/log.md：紀錄要依時間由舊到新排列（新紀錄加在最下面）")

    out = ROOT / "assets/js/wiki-data.js"
    if not out.exists() or out.read_text(encoding="utf-8") != build_wiki.render():
        err("assets/js/wiki-data.js 不是最新的，請執行 python3 scripts/build_wiki.py")
    return len(rw), len(pages)


def check_site():
    for f in [ROOT / "index.html", ROOT / "wiki.html"]:
        rel = f.relative_to(ROOT)
        html = f.read_text(encoding="utf-8")
        if re.search(r'\sstyle="', html) or "<style" in html:
            err(f"{rel}：不可使用 inline style 或 <style>，請寫到 assets/css/style.css")
        for attr in re.findall(r'(?:href|src)="(/[^/"][^"]*)"', html):
            err(f"{rel}：不可使用以 / 開頭的絕對路徑：{attr}")
        if HEX_RE.search(re.sub(r"<!--.*?-->", "", html, flags=re.S)):
            err(f"{rel}：HTML 裡出現寫死的色碼")
    css = re.sub(r"/\*.*?\*/", "", CSS_FILE.read_text(encoding="utf-8"), flags=re.S)
    for hx in HEX_RE.findall(re.sub(r":root\s*\{[^}]*\}", "", css)):
        err(f"style.css：:root 之外出現寫死的色碼 {hx}，請改用 CSS 變數")
    for js in (ROOT / "assets/js").glob("*.js"):
        if "fetch(" in js.read_text(encoding="utf-8"):
            err(f"{js.relative_to(ROOT)}：不要用 fetch() 讀資料（file:// 下會失敗）")
    allowed = {"CLAUDE.md", "AGENTS.md", "README.md", "index.html", "wiki.html", ".nojekyll", ".gitignore",
               "assets", "raw", "wiki", "scripts", ".claude", ".git"}
    for p in ROOT.iterdir():
        if p.name not in allowed:
            err(f"頂層出現未列在 CLAUDE.md 第 4 節的項目：{p.name}")


def main():
    n_words, n_pages = check_wiki()
    check_site()
    for w in warnings:
        print(f"⚠ 提醒：{w}")
    for e in errors:
        print(f"✗ 錯誤：{e}")
    if errors:
        print(f"\n共 {len(errors)} 個錯誤，請修正後再執行一次。")
        sys.exit(1)
    print(f"\n✓ 全部通過（raw 筆記 {n_words} 個字，wiki {n_pages} 頁）")


if __name__ == "__main__":
    main()
