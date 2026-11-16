#!/usr/bin/env python3
"""
把 wiki/ 底下的 Markdown 打包成 assets/js/wiki-data.js，讓網站的知識庫頁（wiki.html）可以讀取。
用法：在專案根目錄執行  python3 scripts/build_wiki.py
每次修改 wiki/ 之後都要執行；scripts/check.py 會檢查打包檔是不是最新的。
只使用 Python 標準函式庫。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = ROOT / "wiki"
OUT_FILE = ROOT / "assets/js/wiki-data.js"

HEADER = (
    "/* 自動產生，請勿手動修改。來源：wiki/*.md，產生方式：python3 scripts/build_wiki.py */\n"
)


def parse_page(path):
    """回傳 (frontmatter dict, body str)。frontmatter 為簡單的 key: value 格式。"""
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = text[end + 5:]
    meta["sources"] = [s.strip() for s in meta.get("sources", "").split(",") if s.strip()]
    return meta, body.strip() + "\n"


def collect():
    pages = {}
    for path in sorted(WIKI_DIR.rglob("*.md")):
        page_id = path.relative_to(WIKI_DIR).with_suffix("").as_posix()
        meta, body = parse_page(path)
        page = {"title": page_id, "type": "", "summary": "", "updated": ""}
        page.update(meta)  # 其他欄位（pos、zh、topic、asked…）也一起輸出給網頁使用
        page["body"] = body
        pages[page_id] = page
    return pages


def render():
    data = json.dumps(collect(), ensure_ascii=False, indent=1, sort_keys=True)
    return HEADER + "window.WIKI = " + data + ";\n"


def main():
    OUT_FILE.write_text(render(), encoding="utf-8")
    print(f"✓ 已產生 {OUT_FILE.relative_to(ROOT)}（{len(collect())} 頁）")


if __name__ == "__main__":
    main()
