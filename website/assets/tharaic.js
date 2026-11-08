// Site-wide display of Tharaic words: Greek script or romanization, and the typeface.
// Every word in Greek script made only of Tharaic letters is wrapped in <span class="th">,
// keeping the original in data-g. Real Greek with accents (λόγος) is left alone.
(function () {
  "use strict";

  // Same tables as tools/greek.py
  var ROMAN = {
    "α": "a", "ᾱ": "ā", "β": "b", "δ": "d", "ε": "e", "η": "ē", "γ": "g", "ͱ": "h",
    "ι": "i", "κ": "k", "λ": "l", "μ": "m", "ν": "n", "ο": "o", "ω": "ō", "π": "p",
    "ρ": "r", "σ": "s", "ς": "s", "τ": "t", "υ": "u", "ῡ": "ū", "ϝ": "v", "ξ": "x",
    "ζ": "z", "φ": "ph", "θ": "th", "χ": "kh", "ϸ": "sh", "ϙ": "gh", "ψ": "ps", "ϳ": "y"
  };
  // Capitals whose lowercase JavaScript does not map the way Python does
  var LOWER = { "Ͱ": "ͱ", "Ϳ": "ϳ", "Ϸ": "ϸ", "Ϙ": "ϙ", "Ϝ": "ϝ", "Ᾱ": "ᾱ", "Ῡ": "ῡ" };
  var RUN = /[Ͱ-Ͽἀ-῿]+/g;
  var KEY = "tharaic-display";

  function lower(c) { return LOWER[c] || c.toLowerCase(); }

  function isTharaic(word) {
    for (var i = 0; i < word.length; i++) if (!ROMAN[lower(word[i])]) return false;
    return true;
  }

  function toRoman(word) {
    var out = "";
    for (var i = 0; i < word.length; i++) {
      var c = word[i], l = lower(c), r = ROMAN[l];
      out += c !== l ? r[0].toUpperCase() + r.slice(1) : r;
    }
    return out;
  }

  var state = { script: "greek", font: "plain" };
  try {
    var saved = JSON.parse(localStorage.getItem(KEY) || "{}");
    if (saved.script === "roman") state.script = "roman";
    if (["stele", "wedge", "ledger"].indexOf(saved.font) >= 0) state.font = saved.font;
  } catch (e) { /* storage blocked: keep the defaults */ }

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* ignore */ }
  }

  var SKIP = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, CODE: 1, PRE: 1, INPUT: 1 };

  // Wrap the Tharaic words under root in spans (once)
  function wrap(root) {
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        for (var p = n.parentNode; p && p !== root; p = p.parentNode) {
          if (SKIP[p.nodeName] || (p.classList && p.classList.contains("th"))) return NodeFilter.FILTER_REJECT;
        }
        RUN.lastIndex = 0;
        return RUN.test(n.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(function (node) {
      var text = node.nodeValue, frag = document.createDocumentFragment(), last = 0, m;
      RUN.lastIndex = 0;
      while ((m = RUN.exec(text))) {
        if (!isTharaic(m[0])) continue;
        if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
        frag.appendChild(word(m[0]));
        last = m.index + m[0].length;
      }
      if (last === 0) return;
      if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
      node.parentNode.replaceChild(frag, node);
    });
  }

  function word(greek) {
    var s = document.createElement("span");
    s.className = "th";
    s.setAttribute("data-g", greek);
    s.setAttribute("lang", "x-tharaic");
    s.textContent = state.script === "roman" ? toRoman(greek) : greek;
    return s;
  }

  function refresh(root) {
    var spans = (root || document).querySelectorAll(".th[data-g]");
    for (var i = 0; i < spans.length; i++) {
      var g = spans[i].getAttribute("data-g");
      spans[i].textContent = state.script === "roman" ? toRoman(g) : g;
    }
    document.documentElement.setAttribute("data-th-font", state.font);
    document.documentElement.setAttribute("data-th-script", state.script);
    var buttons = document.querySelectorAll("[data-th-script], [data-th-font]");
    for (var j = 0; j < buttons.length; j++) {
      var b = buttons[j];
      var on = b.getAttribute("data-th-script") === state.script || b.getAttribute("data-th-font") === state.font;
      b.setAttribute("aria-pressed", on ? "true" : "false");
    }
  }

  document.addEventListener("click", function (ev) {
    var b = ev.target.closest && ev.target.closest("button[data-th-script], button[data-th-font]");
    if (!b) return;
    if (b.hasAttribute("data-th-script")) state.script = b.getAttribute("data-th-script");
    else state.font = b.getAttribute("data-th-font");
    save();
    refresh();
  });

  function start() {
    var content = document.querySelector(".md-content__inner") || document.body;
    wrap(content);
    refresh();
  }

  window.Tharaic = { word: word, toRoman: toRoman, isTharaic: isTharaic, refresh: refresh, state: state };
  document.documentElement.setAttribute("data-th-font", state.font);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
