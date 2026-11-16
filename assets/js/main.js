/*
 * main.js — 首頁渲染（資料來自 window.WIKI，由 scripts/build_wiki.py 從 wiki/*.md 產生）
 * 首頁不另外存資料：主題、單字、問答全部讀 wiki 的 frontmatter（單一資料來源）。
 */
(function () {
  "use strict";

  var year = document.querySelector("[data-year]");
  if (year) year.textContent = new Date().getFullYear();
  if (document.body.dataset.page !== "home") return;

  var WIKI = window.WIKI || {};
  function byType(t) {
    return Object.keys(WIKI).filter(function (id) { return WIKI[id].type === t; })
      .map(function (id) { return Object.assign({ id: id }, WIKI[id]); });
  }
  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") n.textContent = attrs[k]; else if (k === "class") n.className = attrs[k]; else n.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) n.appendChild(c); });
    return n;
  }
  function wikiUrl(id) { return "wiki.html#" + id; }

  var topics = byType("topic").sort(function (a, b) { return a.title.localeCompare(b.title); });
  var words = byType("word").sort(function (a, b) { return a.title.localeCompare(b.title); });
  var queries = byType("query").sort(function (a, b) { return (b.asked || "").localeCompare(a.asked || ""); });
  var topicName = {};
  topics.forEach(function (t) { topicName[t.id.split("/")[1]] = t.title; });

  // 統計
  var stats = document.querySelector("[data-stats]");
  [["單字", words.length], ["主題", topics.length], ["問答", queries.length], ["知識庫頁面", Object.keys(WIKI).length]].forEach(function (s) {
    stats.appendChild(el("div", {}, [el("dt", { text: s[0] }), el("dd", { text: String(s[1]) })]));
  });

  // 主題卡片
  var topicBox = document.querySelector("[data-topics]");
  topics.forEach(function (t) {
    var n = words.filter(function (w) { return w.topic === t.id.split("/")[1]; }).length;
    topicBox.appendChild(el("a", { class: "topic-card", href: wikiUrl(t.id) }, [
      el("p", { class: "card-meta", text: n + " words" }),
      el("h3", { text: t.title }),
      el("p", { class: "summary", text: t.summary })
    ]));
  });

  // 單字卡片 + 篩選 + 搜尋
  var grid = document.querySelector("[data-words]");
  var search = document.querySelector("[data-word-search]");
  var filterBox = document.querySelector("[data-filters]");
  var currentTopic = "all";

  function draw() {
    var q = (search.value || "").trim().toLowerCase();
    grid.innerHTML = "";
    var list = words.filter(function (w) {
      return (currentTopic === "all" || w.topic === currentTopic) &&
        (!q || (w.title + " " + w.zh).toLowerCase().indexOf(q) >= 0);
    });
    if (!list.length) {
      grid.appendChild(el("p", { class: "empty-note", text: "知識庫裡沒有符合的單字。要新增，請把筆記放進 raw/vocab/ 再 ingest。" }));
      return;
    }
    list.forEach(function (w) {
      grid.appendChild(el("a", { class: "word-card", href: wikiUrl(w.id) }, [
        el("p", { class: "word-card-meta", text: w.pos + " · " + (topicName[w.topic] || w.topic).split(" ")[0] }),
        el("h3", { text: w.title }),
        el("p", { class: "word-zh", text: w.zh })
      ]));
    });
  }

  [["all", "全部"]].concat(topics.map(function (t) { return [t.id.split("/")[1], t.title.split(" ")[0]]; })).forEach(function (f, i) {
    var btn = el("button", { class: "filter-btn", type: "button", "aria-pressed": i === 0 ? "true" : "false", text: f[1] });
    btn.addEventListener("click", function () {
      filterBox.querySelectorAll(".filter-btn").forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
      btn.setAttribute("aria-pressed", "true");
      currentTopic = f[0];
      draw();
    });
    filterBox.appendChild(btn);
  });
  search.addEventListener("input", draw);
  draw();

  // 問答紀錄
  var qBox = document.querySelector("[data-queries]");
  queries.forEach(function (q) {
    qBox.appendChild(el("li", {}, [el("a", { href: wikiUrl(q.id) }, [
      el("span", { class: "q-mark", text: "Q" }),
      el("span", { class: "q-text" }, [el("strong", { text: q.title }), el("small", { text: q.summary })])
    ])]));
  });
})();
