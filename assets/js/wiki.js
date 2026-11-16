/*
 * wiki.js — 知識庫頁（wiki.html）的渲染程式
 * 資料來自 window.WIKI（由 scripts/build_wiki.py 從 wiki/*.md 產生）
 * 網址格式：wiki.html#<頁面 id>，例如 wiki.html#words/mitigate
 */
(function () {
  "use strict";

  var WIKI = window.WIKI || {};
  var TYPE_LABELS = { index: "目錄", log: "操作紀錄", topic: "主題", word: "單字", concept: "學習方法", query: "問答紀錄" };
  var GROUPS = [["總覽", ["index", "log"]], ["主題", ["topic"]], ["單字", ["word"]], ["學習方法", ["concept"]], ["問答紀錄", ["query"]]];

  /* ---------- 路徑處理 ---------- */
  function dirOf(id) { var i = id.lastIndexOf("/"); return i < 0 ? "wiki" : "wiki/" + id.slice(0, i); }

  function resolvePath(baseDir, href) {
    var parts = baseDir ? baseDir.split("/") : [];
    href.split("/").forEach(function (p) {
      if (p === "..") parts.pop();
      else if (p !== "." && p !== "") parts.push(p);
    });
    return parts.join("/");
  }

  // 把 wiki 頁面裡的相對連結轉成網站上可用的連結
  function rewriteHref(pageId, href) {
    if (/^(https?:|mailto:|#)/.test(href)) return { href: href, external: /^https?:/.test(href) };
    var full = resolvePath(dirOf(pageId), href);
    if (/^wiki\/.+\.md$/.test(full)) return { href: "#" + full.slice(5, -3), id: full.slice(5, -3) };
    return { href: full };
  }

  /* ---------- 極簡 Markdown 渲染 ---------- */
  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function inline(text, pageId) {
    var codes = [];
    var s = esc(text).replace(/`([^`]+)`/g, function (_, c) { codes.push(c); return "\u0000" + (codes.length - 1) + "\u0000"; });
    s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, function (_, label, href) {
      var r = rewriteHref(pageId, href.replace(/&amp;/g, "&"));
      return '<a href="' + esc(r.href) + '"' + (r.external ? ' target="_blank" rel="noopener"' : "") + ">" + label + "</a>";
    });
    return s.replace(/\u0000(\d+)\u0000/g, function (_, i) { return "<code>" + codes[+i] + "</code>"; });
  }

  function splitRow(line) {
    return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(function (c) { return c.trim(); });
  }

  function markdown(src, pageId) {
    var lines = src.split("\n"), out = [], i = 0, para = [];
    function flush() { if (para.length) { out.push("<p>" + inline(para.join(" "), pageId) + "</p>"); para = []; } }

    while (i < lines.length) {
      var line = lines[i];
      if (/^```/.test(line)) {
        flush(); var code = []; i++;
        while (i < lines.length && !/^```/.test(lines[i])) code.push(lines[i++]);
        out.push("<pre><code>" + esc(code.join("\n")) + "</code></pre>"); i++; continue;
      }
      var h = line.match(/^(#{1,3})\s+(.*)/);
      if (h) { flush(); var lv = Math.min(h[1].length + 1, 4); out.push("<h" + lv + ">" + inline(h[2], pageId) + "</h" + lv + ">"); i++; continue; }
      if (/^\|/.test(line) && /^\|[\s:|-]+\|?\s*$/.test(lines[i + 1] || "")) {
        flush();
        var head = splitRow(line), rows = []; i += 2;
        while (i < lines.length && /^\|/.test(lines[i])) rows.push(splitRow(lines[i++]));
        out.push('<div class="table-wrap"><table><thead><tr>' + head.map(function (c) { return "<th>" + inline(c, pageId) + "</th>"; }).join("") +
          "</tr></thead><tbody>" + rows.map(function (r) { return "<tr>" + r.map(function (c) { return "<td>" + inline(c, pageId) + "</td>"; }).join("") + "</tr>"; }).join("") +
          "</tbody></table></div>");
        continue;
      }
      if (/^[-*]\s+/.test(line) || /^\d+\.\s+/.test(line)) {
        flush();
        var ordered = /^\d+\./.test(line), items = [], re = ordered ? /^\d+\.\s+/ : /^[-*]\s+/;
        while (i < lines.length && re.test(lines[i])) items.push(lines[i++].replace(re, ""));
        var tag = ordered ? "ol" : "ul";
        out.push("<" + tag + ">" + items.map(function (t) { return "<li>" + inline(t, pageId) + "</li>"; }).join("") + "</" + tag + ">");
        continue;
      }
      if (/^>\s?/.test(line)) {
        flush(); var q = [];
        while (i < lines.length && /^>\s?/.test(lines[i])) q.push(lines[i++].replace(/^>\s?/, ""));
        out.push("<blockquote><p>" + inline(q.join(" "), pageId) + "</p></blockquote>"); continue;
      }
      if (/^---+\s*$/.test(line)) { flush(); out.push("<hr>"); i++; continue; }
      if (!line.trim()) { flush(); i++; continue; }
      para.push(line.trim()); i++;
    }
    flush();
    return out.join("\n");
  }

  /* ---------- 反向連結 ---------- */
  var backlinks = {};
  Object.keys(WIKI).forEach(function (id) {
    var re = /\]\(([^)\s]+\.md)\)/g, m;
    while ((m = re.exec(WIKI[id].body))) {
      var target = rewriteHref(id, m[1]).id;
      if (target && target !== id) {
        backlinks[target] = backlinks[target] || [];
        if (backlinks[target].indexOf(id) < 0) backlinks[target].push(id);
      }
    }
  });

  /* ---------- 畫面 ---------- */
  var nav = document.querySelector("[data-wiki-nav]");
  var article = document.querySelector("[data-wiki-article]");
  var search = document.querySelector("[data-wiki-search]");

  function buildNav(filter) {
    nav.innerHTML = "";
    var q = (filter || "").trim().toLowerCase();
    GROUPS.forEach(function (g) {
      var ids = Object.keys(WIKI).filter(function (id) {
        var p = WIKI[id];
        return g[1].indexOf(p.type) >= 0 && (!q || (p.title + p.summary).toLowerCase().indexOf(q) >= 0);
      }).sort(function (a, b) {
        if (g[0] === "總覽") return a === "index" ? -1 : 1;
        return WIKI[a].title.localeCompare(WIKI[b].title, "zh-Hant");
      });
      if (!ids.length) return;
      var html = '<p class="wiki-nav-group">' + g[0] + " <span>" + ids.length + "</span></p><ul>";
      ids.forEach(function (id) { html += '<li><a href="#' + id + '" data-id="' + id + '">' + esc(WIKI[id].title) + "</a></li>"; });
      nav.insertAdjacentHTML("beforeend", html + "</ul>");
    });
    markCurrent();
  }

  function currentId() {
    var id = decodeURIComponent(location.hash.slice(1));
    return WIKI[id] ? id : "index";
  }

  function markCurrent() {
    var id = currentId();
    nav.querySelectorAll("a").forEach(function (a) {
      if (a.dataset.id === id) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
  }

  function render() {
    var id = currentId(), p = WIKI[id];
    if (!p) { article.innerHTML = '<p class="todo">知識庫是空的，請執行 python3 scripts/build_wiki.py。</p>'; return; }
    var html = '<p class="eyebrow">' + (TYPE_LABELS[p.type] || p.type) + " · wiki/" + esc(id) + ".md</p>";
    html += "<h1>" + esc(p.title) + "</h1>";
    if (p.summary && p.type !== "index" && p.type !== "log") html += '<p class="wiki-summary">' + esc(p.summary) + "</p>";
    html += '<div class="wiki-meta">' + (p.asked ? "提問 " + esc(p.asked) + " · " : "") + "更新 " + esc(p.updated) +
      ((p.sources || []).length ? " · 來源：" + p.sources.map(function (s) { return '<a href="' + esc(s) + '">' + esc(s.replace(/^raw\//, "")) + "</a>"; }).join("、") : "") + "</div>";
    html += '<div class="wiki-body">' + markdown(p.body, id) + "</div>";
    var bl = backlinks[id] || [];
    if (bl.length && p.type !== "index") {
      html += '<aside class="wiki-backlinks"><h2>被這些頁面引用</h2><ul>' +
        bl.map(function (b) { return '<li><a href="#' + b + '">' + esc(WIKI[b].title) + "</a> <span>" + (TYPE_LABELS[WIKI[b].type] || "") + "</span></li>"; }).join("") +
        "</ul></aside>";
    }
    article.innerHTML = html;
    document.title = p.title + "｜IELTS 單字知識庫";
    markCurrent();
  }

  if (search) search.addEventListener("input", function () { buildNav(search.value); });
  window.addEventListener("hashchange", function () { render(); window.scrollTo(0, 0); });

  var count = document.querySelector("[data-wiki-count]");
  if (count) count.textContent = Object.keys(WIKI).length;

  buildNav("");
  render();
})();
