// English → Tharaic word-by-word lookup (website/lookup.md).
// Uses assets/lexicon.json, made from data/lexicon.yaml by tools/export_lexicon.py.
(function () {
  "use strict";

  var root = document.getElementById("th-lookup");
  if (!root) return;

  var input = document.getElementById("th-lookup-input");
  var output = document.getElementById("th-lookup-output");
  var detail = document.getElementById("th-lookup-detail");
  var lexicon = null, register = "everyday", tokens = [];

  // English forms the suffix rules below cannot undo
  var IRREGULAR = {
    am: "be", is: "be", are: "be", was: "be", were: "be", been: "be", being: "be",
    has: "have", had: "have", does: "do", did: "do", done: "do", went: "go", gone: "go",
    saw: "see", seen: "see", came: "come", gave: "give", given: "give", took: "take",
    taken: "take", made: "make", said: "say", knew: "know", known: "know", ate: "eat",
    eaten: "eat", drank: "drink", drunk: "drink", spoke: "speak", spoken: "speak",
    wrote: "write", written: "write", ran: "run", sat: "sit", stood: "stand", told: "tell",
    found: "find", brought: "bring", bought: "buy", sold: "sell", thought: "think",
    taught: "teach", caught: "catch", fought: "fight", held: "hold", kept: "keep",
    slept: "sleep", felt: "feel", met: "meet", heard: "hear", built: "build", sent: "send",
    spent: "spend", lost: "lose", fell: "fall", fallen: "fall", flew: "fly", grew: "grow",
    threw: "throw", drew: "draw", blew: "blow", sang: "sing", sung: "sing", began: "begin",
    begun: "begin", swam: "swim", rode: "ride", rose: "rise", risen: "rise", broke: "break",
    broken: "break", chose: "choose", wore: "wear", bore: "bear", born: "bear",
    struck: "strike", hid: "hide", led: "lead", fed: "feed", shot: "shoot", won: "win",
    sank: "sink", sunk: "sink", stole: "steal", forgot: "forget", forgave: "forgive",
    understood: "understand", got: "get", lay: "lie", laid: "lay", paid: "pay", fled: "flee",
    men: "man", women: "woman", children: "child", feet: "foot", teeth: "tooth",
    mice: "mouse", oxen: "ox", geese: "goose", better: "good", best: "good",
    worse: "bad", worst: "bad", me: "i", him: "he", her: "she", us: "we", them: "they",
    towards: "toward", upon: "on", into: "in"
  };
  var CONTRACTIONS = {
    "won't": ["will", "not"], "can't": ["can", "not"], "shan't": ["shall", "not"],
    "cannot": ["can", "not"]
  };
  var ARTICLES = { the: 1, a: 1, an: 1 };
  var POSSESSIVE = { my: 1, your: 1, his: 1, her: 1, its: 1, our: 1, their: 1 };
  var AUXILIARY = { "do": 1, does: 1, did: 1 };

  function undouble(b) { return /(.)\1$/.test(b) ? b.slice(0, -1) : b; }

  // Possible dictionary forms of an English word, most likely first
  function stems(w) {
    var out = [];
    function add(x) { if (x && x.length > 1 && out.indexOf(x) < 0) out.push(x); }
    out.push(w);
    if (IRREGULAR[w]) add(IRREGULAR[w]);
    var b;
    if (/ies$/.test(w)) add(w.slice(0, -3) + "y");
    if (/ves$/.test(w)) { add(w.slice(0, -3) + "f"); add(w.slice(0, -3) + "fe"); }
    if (/(s|x|z|ch|sh|o)es$/.test(w)) add(w.slice(0, -2));
    if (/[^s]s$/.test(w)) add(w.slice(0, -1));
    if (/ied$/.test(w)) add(w.slice(0, -3) + "y");
    if (/ed$/.test(w)) { b = w.slice(0, -2); add(b); add(b + "e"); add(undouble(b)); }
    if (/ying$/.test(w)) add(w.slice(0, -4) + "ie");
    if (/ing$/.test(w)) { b = w.slice(0, -3); add(b); add(b + "e"); add(undouble(b)); }
    if (/ier$/.test(w)) add(w.slice(0, -3) + "y");
    if (/iest$/.test(w)) add(w.slice(0, -4) + "y");
    if (/er$/.test(w)) { b = w.slice(0, -2); add(b); add(b + "e"); add(undouble(b)); }
    if (/est$/.test(w)) { b = w.slice(0, -3); add(b); add(b + "e"); add(undouble(b)); }
    if (/ily$/.test(w)) add(w.slice(0, -3) + "y");
    if (/ly$/.test(w)) add(w.slice(0, -2));
    return out;
  }

  // Split English into words and punctuation; expand contractions
  function tokenize(text) {
    var out = [], re = /[A-Za-z]+(?:['’][A-Za-z]+)*|\d+|\S/g, m;
    while ((m = re.exec(text))) {
      var t = m[0], low = t.toLowerCase().replace(/’/g, "'");
      if (!/^[a-z]/.test(low)) { out.push({ text: t, punct: !/^\d/.test(t), word: false }); continue; }
      var parts;
      if (CONTRACTIONS[low]) parts = CONTRACTIONS[low];
      else if (/n't$/.test(low)) parts = [low.slice(0, -3), "not"];
      else if (/'ll$/.test(low)) parts = [low.slice(0, -3), "will"];
      else if (/'re$/.test(low)) parts = [low.slice(0, -3), "are"];
      else if (/'ve$/.test(low)) parts = [low.slice(0, -3), "have"];
      else if (/'m$/.test(low)) parts = [low.slice(0, -2), "am"];
      else if (/'[sd]$/.test(low)) parts = [low.slice(0, -2)];
      else parts = [low];
      for (var i = 0; i < parts.length; i++) out.push({ text: i ? parts[i] : t, low: parts[i], word: true });
    }
    return out;
  }

  // Lexicon entries for an English key, best first for the chosen register
  function candidates(key) {
    var hits = lexicon.keys[key];
    if (!hits) return null;
    var list = hits.map(function (h, order) { return { e: lexicon.entries[h[0]], n: h[0], pos: h[1], order: order }; });
    var standard = list.filter(function (c) { return !c.e.dia; });
    if (standard.length) list = standard;
    function score(c) {
      var reg = c.e.reg;
      if (register === "high") return reg === "high" ? 0 : reg === "everyday" ? 2 : 1;
      return reg === "high" ? 2 : 0;
    }
    list.sort(function (a, b) { return score(a) - score(b) || a.pos - b.pos || a.order - b.order; });
    return list;
  }

  function find(words) {
    for (var i = 0; i < words.length; i++) {
      var forms = stems(words[i]);
      for (var j = 0; j < forms.length; j++) {
        var c = candidates(forms[j]);
        if (c) return { key: forms[j], list: c };
      }
    }
    return null;
  }

  // How an English word was reduced to its key: "verb" for -ed, -ing and irregular
  // verb forms, "s" for a final -s, which may be a plural or a verb ending
  function suffix(word, key) {
    if (word === key) return "";
    if (/(ed|ing)$/.test(word) || (IRREGULAR[word] === key && /^[a-z]+$/.test(key) && !/^(i|he|she|we|they|good|bad|toward|on|in)$/.test(key) && !/(men|ren|eet|eeth|ice|xen|eese)$/.test(word))) return "verb";
    return /s$/.test(word) ? "s" : "";
  }

  // Many English words are both noun and verb ("sail"). Guess from the word before
  // which one is meant, and put the first candidate of that kind first.
  function preferByContext(out) {
    for (var j = 0; j < out.length; j++) {
      var t = out[j];
      if (t.kind !== "word") continue;
      var kinds = t.list.map(function (c) { return c.e.p; });
      if (kinds.indexOf("noun") < 0 || kinds.indexOf("verb") < 0) continue;
      var prev = out[j - 1], want = null;
      if (prev && prev.kind === "skip") {
        want = ARTICLES[prev.text.toLowerCase()] ? "noun" : "verb";
      } else if (prev && prev.kind === "word") {
        var pp = prev.list[prev.choice].e.p, low = prev.text.toLowerCase();
        if (pp === "adj" || pp === "num") want = "noun";
        else if (pp === "pron" || prev.key === "future particle" || prev.key === "not" || low === "to") want = "verb";
        else if (pp === "noun" && t.via === "s") want = "verb";
      } else if (prev && prev.kind === "unknown" && POSSESSIVE[prev.text.toLowerCase()]) {
        want = "noun";
      }
      if (!want && t.via === "verb") want = "verb";
      if (!want) continue;
      t.list = t.list.filter(function (c) { return c.e.p === want; })
        .concat(t.list.filter(function (c) { return c.e.p !== want; }));
    }
  }

  // Longest match of up to three words starting at token i
  function match(toks, i) {
    for (var n = 3; n >= 1; n--) {
      var words = [];
      for (var k = i; k < i + n && k < toks.length && toks[k].word; k++) words.push(toks[k].low);
      if (words.length < n) continue;
      var head = words.slice(0, -1).join(" "), last = words[n - 1];
      var forms = stems(last);
      for (var j = 0; j < forms.length; j++) {
        var key = (head ? head + " " : "") + forms[j], c = candidates(key);
        if (c) return { n: n, key: key, list: c, via: suffix(last, forms[j]) };
      }
    }
    return null;
  }

  function lookup(text) {
    var toks = tokenize(text), out = [];
    for (var i = 0; i < toks.length; i++) {
      var t = toks[i];
      if (!t.word) { out.push({ kind: "text", text: t.text, punct: t.punct }); continue; }
      var next = toks[i + 1], prev = toks[i - 1];
      var first = !prev || (prev.punct && /[.!?;:]/.test(prev.text));
      if (ARTICLES[t.low]) { out.push({ kind: "skip", text: t.text, why: "no separate word in Tharaic" }); continue; }
      if (AUXILIARY[t.low] && next && next.word && (next.low === "not" || first)) {
        out.push({ kind: "skip", text: t.text, why: "helper verb, not translated" }); continue;
      }
      var m;
      if ((t.low === "will" || t.low === "shall") && next && next.word) {
        m = { n: 1, key: "future particle", list: candidates("future particle") };
      } else if (t.low === "to") {
        m = { n: 1, key: "toward", list: candidates("toward") };
      } else {
        m = match(toks, i);
      }
      if (!m) { out.push({ kind: "unknown", text: t.text }); continue; }
      var english = toks.slice(i, i + m.n).map(function (x) { return x.text; }).join(" ");
      out.push({ kind: "word", text: english, key: m.key, list: m.list, choice: 0, via: m.via || "" });
      i += m.n - 1;
    }
    preferByContext(out);
    // "to" before a verb marks the infinitive: drop it; otherwise it means "toward"
    for (var j = 0; j < out.length; j++) {
      if (out[j].kind !== "word" || out[j].key !== "toward" || out[j].text.toLowerCase() !== "to") continue;
      var after = out[j + 1];
      if (after && after.kind === "word" && after.list[after.choice].e.p === "verb") {
        out[j] = { kind: "skip", text: out[j].text, why: "marks the infinitive, not translated" };
      }
    }
    return out;
  }

  function headword(e) { return e.g.split(" / ")[0]; }

  function tharaic(e) {
    var s = window.Tharaic ? window.Tharaic.word(headword(e)) : document.createElement("span");
    if (!window.Tharaic) s.textContent = headword(e);
    return s;
  }

  function el(tag, cls, text) {
    var x = document.createElement(tag);
    if (cls) x.className = cls;
    if (text != null) x.textContent = text;
    return x;
  }

  function renderOutput() {
    output.textContent = "";
    var started = false;
    tokens.forEach(function (t) {
      if (t.kind === "skip") return;
      if (started && !(t.kind === "text" && t.punct && /^[.,!?;:)\]»]$/.test(t.text))) output.appendChild(document.createTextNode(" "));
      started = true;
      if (t.kind === "word") {
        var e = t.list[t.choice].e, s = tharaic(e);
        s.title = t.text + " — " + e.m;
        output.appendChild(s);
      } else if (t.kind === "unknown") {
        output.appendChild(el("span", "th-lookup__unknown", "[" + t.text + "]"));
      } else {
        output.appendChild(document.createTextNode(t.text));
      }
    });
  }

  function renderDetail() {
    detail.textContent = "";
    var rows = tokens.filter(function (t) { return t.kind !== "text"; });
    if (!rows.length) return;
    var table = el("table");
    var head = el("tr");
    ["English", "Tharaic", "Meaning", "Other words"].forEach(function (h) { head.appendChild(el("th", null, h)); });
    var thead = el("thead"); thead.appendChild(head); table.appendChild(thead);
    var body = el("tbody");
    rows.forEach(function (t) {
      var tr = el("tr");
      tr.appendChild(el("td", null, t.text));
      if (t.kind === "word") {
        var c = t.list[t.choice], e = c.e;
        var cell = el("td"), a = el("a");
        a.href = "lexicon.html#" + e.sec;
        a.appendChild(tharaic(e));
        cell.appendChild(a);
        cell.appendChild(el("div", "th-lookup__meta", [e.gr, e.reg, e.dia].filter(Boolean).join(" · ")));
        tr.appendChild(cell);
        tr.appendChild(el("td", null, e.m));
        var alts = el("td");
        t.list.forEach(function (o, k) {
          if (k === t.choice) return;
          var b = el("button", "th-lookup__alt");
          b.type = "button";
          b.title = o.e.m;
          b.appendChild(tharaic(o.e));
          if (o.e.reg) b.appendChild(document.createTextNode(" " + o.e.reg));
          b.addEventListener("click", function () { t.choice = k; render(); });
          alts.appendChild(b);
        });
        tr.appendChild(alts);
      } else if (t.kind === "unknown") {
        var miss = el("td");
        miss.colSpan = 3;
        miss.appendChild(document.createTextNode("Not in the lexicon. Try a simpler or more common word, or browse the "));
        var link = el("a", null, "English index");
        link.href = "english-index.html";
        miss.appendChild(link);
        miss.appendChild(document.createTextNode("."));
        tr.appendChild(miss);
      } else {
        var skip = el("td", "th-lookup__meta", "— (" + t.why + ")");
        skip.colSpan = 3;
        tr.appendChild(skip);
      }
      body.appendChild(tr);
    });
    table.appendChild(body);
    var wrap = el("div", "md-typeset__table"); wrap.appendChild(table);
    detail.appendChild(wrap);
  }

  function render() {
    renderOutput();
    renderDetail();
    if (window.Tharaic) window.Tharaic.refresh(root);
  }

  function run() {
    if (!lexicon) return;
    tokens = lookup(input.value);
    render();
  }

  function setRegister(r) {
    register = r;
    var bs = root.querySelectorAll("[data-th-register]");
    for (var i = 0; i < bs.length; i++) bs[i].setAttribute("aria-pressed", bs[i].getAttribute("data-th-register") === r ? "true" : "false");
  }

  document.getElementById("th-lookup-go").addEventListener("click", run);
  input.addEventListener("keydown", function (ev) {
    if (ev.key === "Enter" && (ev.ctrlKey || ev.metaKey)) { ev.preventDefault(); run(); }
  });
  root.addEventListener("click", function (ev) {
    var b = ev.target.closest("[data-th-register]");
    if (b) { setRegister(b.getAttribute("data-th-register")); run(); }
  });
  document.getElementById("th-lookup-copy").addEventListener("click", function () {
    var text = output.textContent;
    if (navigator.clipboard && text) navigator.clipboard.writeText(text).catch(function () {});
  });

  try {
    var q = new URLSearchParams(location.search).get("q");
    if (q) input.value = q;
  } catch (e) { /* old browser: keep the example */ }

  output.textContent = "Loading the lexicon…";
  fetch("assets/lexicon.json")
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (data) { lexicon = data; output.textContent = ""; run(); })
    .catch(function () { output.textContent = "The lexicon could not be loaded. Reload the page to try again."; });

  // Exposed for testing
  window.TharaicLookup = { lookup: function (text) { return lexicon ? lookup(text) : null; }, stems: stems };
})();
