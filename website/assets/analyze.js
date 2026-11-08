// Tharaic → English: click a Tharaic word on any page to see what it is.
// Uses assets/forms.json (every form tools/inflect.py generates) and assets/lexicon.json,
// both made by tools/export_lexicon.py, loaded on the first click. The analysis follows
// Index.analyze in tools/inflect.py: prefixes and object enclitics after hyphens,
// possessive enclitics on nouns.
(function () {
  "use strict";

  var T = window.Tharaic;
  if (!T) return;

  var CASES = ["NOM", "ACC", "GEN", "DAT", "VOC", "LOC", "INS", "ABL"];
  var WORDS = {
    NOM: "nominative", ACC: "accusative", GEN: "genitive", DAT: "dative", VOC: "vocative",
    LOC: "locative", INS: "instrumental", ABL: "ablative", SG: "singular", DU: "dual",
    PL: "plural", AN: "animate", IN: "inanimate", CONSTR: "construct", PRES: "present",
    AOR: "aorist", MID: "middle", PTCP: "participle", INF: "infinitive", IMP: "imperative",
    COMP: "comparative", SUPL: "superlative", "1SG": "1st person singular",
    "2SG": "2nd person singular", "3SG": "3rd person singular", "1PL": "1st person plural",
    "2PL": "2nd person plural", "3PL": "3rd person plural"
  };

  var pop = null, current = null;

  function norm(w) {
    var out = "";
    for (var i = 0; i < w.length; i++) out += T.lower(w[i]);
    return out.replace(/ς/g, "σ");
  }

  function nominal(tag) {
    if (!tag) return false;
    var parts = tag.split(" ");
    var first = parts[parts.length - 1].split(".")[0];
    return CASES.indexOf(first) >= 0 || first === "AN" || first === "IN" || first === "CONSTR";
  }

  // [{lemma, tag, poss}] for one word without hyphens
  function lookup(w, F) {
    var found = [];
    (F.forms[w] || []).forEach(function (p) { found.push({ lemma: p[0], tag: F.tags[p[1]], poss: "" }); });
    Object.keys(F.possessive).forEach(function (enc) {
      if (w.length > enc.length + 1 && w.slice(-enc.length) === enc) {
        (F.forms[w.slice(0, -enc.length)] || []).forEach(function (p) {
          var tag = F.tags[p[1]];
          if (nominal(tag)) found.push({ lemma: p[0], tag: tag, poss: enc });
        });
      }
    });
    return found;
  }

  // Analysis of a written token such as ϸε-εσι-υ
  function analyze(token, F) {
    var parts = token.split("-").filter(Boolean).map(norm), prefixes = [], enclitics = [];
    while (parts.length > 1 && F.prefixes.indexOf(parts[0]) >= 0) prefixes.push(parts.shift());
    while (parts.length > 1 && F.object[parts[parts.length - 1]]) enclitics.unshift(parts.pop());
    var found = parts.length === 1 ? lookup(parts[0], F) : [];
    return { stem: parts.join("-"), found: found, prefixes: prefixes, enclitics: enclitics };
  }

  function describe(tag) {
    if (!tag) return "dictionary form";
    return tag.split(" ").map(function (group) {
      if (/^ε\(σ\)-$/.test(group)) return "from the stem ε(σ)-";
      return group.split(".").map(function (x) { return WORDS[x] || x; }).join(" ");
    }).join(", ");
  }

  // The whole hyphenated token a clicked span belongs to: ϸε - εσι - υ
  function tokenSpans(span) {
    var spans = [span], n;
    for (n = span; n.previousSibling && n.previousSibling.nodeType === 3 && n.previousSibling.nodeValue === "-" &&
         n.previousSibling.previousSibling && n.previousSibling.previousSibling.classList &&
         n.previousSibling.previousSibling.classList.contains("th"); n = n.previousSibling.previousSibling) {
      spans.unshift(n.previousSibling.previousSibling);
    }
    for (n = span; n.nextSibling && n.nextSibling.nodeType === 3 && n.nextSibling.nodeValue === "-" &&
         n.nextSibling.nextSibling && n.nextSibling.nextSibling.classList &&
         n.nextSibling.nextSibling.classList.contains("th"); n = n.nextSibling.nextSibling) {
      spans.push(n.nextSibling.nextSibling);
    }
    return spans;
  }

  function el(tag, cls, text) {
    var x = document.createElement(tag);
    if (cls) x.className = cls;
    if (text != null) x.textContent = text;
    return x;
  }

  function both(greek) {
    var s = el("span", null, greek + " ");
    s.appendChild(el("span", "th-pop__roman", T.toRoman(greek)));
    return s;
  }

  function entryLine(box, e, lemmaText) {
    var line = el("div", "th-pop__lemma");
    var a = el("a");
    a.href = "lexicon.html#" + e.sec;
    a.appendChild(both(lemmaText || e.g));
    line.appendChild(a);
    line.appendChild(document.createTextNode(" — " + e.m));
    box.appendChild(line);
    box.appendChild(el("div", "th-pop__meta", [e.gr, e.reg, e.dia].filter(Boolean).join(" · ")));
  }

  function fill(box, token, F, L) {
    var r = analyze(token, F);
    var head = el("div", "th-pop__word");
    head.appendChild(both(token));
    box.appendChild(head);

    r.prefixes.forEach(function (p) {
      var e = L.entries.filter(function (x) { return x.g === p + "-"; })[0];
      var line = el("div", "th-pop__affix");
      line.appendChild(el("strong", null, p + "-"));
      line.appendChild(document.createTextNode(" " + (e ? e.m : "prefix")));
      box.appendChild(line);
    });

    if (!r.found.length) {
      box.appendChild(el("p", "th-pop__none",
        "No analysis found. It may be a chant or dialect form, a word cited as an example, or a form the inflection rules do not produce."));
    }

    // Group the analyses by lemma, keeping their order
    var groups = [], byLemma = {};
    r.found.forEach(function (f) {
      if (!byLemma[f.lemma]) { byLemma[f.lemma] = []; groups.push(f.lemma); }
      byLemma[f.lemma].push(f);
    });
    groups.forEach(function (n) {
      var lemma = F.lemmas[n], block = el("div", "th-pop__block");
      if (lemma[1].length) {
        lemma[1].forEach(function (i) { entryLine(block, L.entries[i]); });
      } else {
        var line = el("div", "th-pop__lemma");
        var a = el("a");
        a.href = "gospels.html#names";
        a.appendChild(both(lemma[0]));
        line.appendChild(a);
        line.appendChild(document.createTextNode(" — " + (lemma[2] || "name")));
        block.appendChild(line);
        block.appendChild(el("div", "th-pop__meta", "proper name"));
      }
      var list = el("ul", "th-pop__tags"), seen = {};
      byLemma[n].forEach(function (f) {
        var text = describe(f.tag) + (f.poss ? " + -" + f.poss + " “" + F.possessive[f.poss] + "”" : "");
        if (seen[text]) return;
        seen[text] = 1;
        var li = el("li", null, text);
        if (f.tag) li.appendChild(el("code", null, f.tag));
        list.appendChild(li);
      });
      block.appendChild(list);
      box.appendChild(block);
    });

    r.enclitics.forEach(function (enc) {
      var line = el("div", "th-pop__affix");
      line.appendChild(el("strong", null, "-" + enc));
      line.appendChild(document.createTextNode(" object pronoun “" + F.object[enc] + "”"));
      box.appendChild(line);
    });
  }

  function close(refocus) {
    if (!pop) return;
    pop.remove();
    pop = null;
    if (current) {
      current.setAttribute("aria-expanded", "false");
      if (refocus) current.focus();
    }
    current = null;
  }

  function place(span) {
    var rect = span.getBoundingClientRect();
    var width = pop.offsetWidth, vw = document.documentElement.clientWidth;
    var left = Math.max(8, Math.min(rect.left, vw - width - 8));
    pop.style.left = (left + window.scrollX) + "px";
    pop.style.top = (rect.bottom + window.scrollY + 6) + "px";
  }

  function open(span) {
    if (current === span) { close(false); return; }
    close(false);
    current = span;
    span.setAttribute("aria-expanded", "true");
    var token = tokenSpans(span).map(function (s) { return s.getAttribute("data-g"); }).join("-");
    pop = el("div", "th-pop md-typeset");
    pop.setAttribute("role", "dialog");
    pop.setAttribute("aria-label", "Analysis of " + token);
    var x = el("button", "th-pop__close", "×");
    x.type = "button";
    x.setAttribute("aria-label", "Close");
    x.addEventListener("click", function () { close(true); });
    pop.appendChild(x);
    var body = el("div", "th-pop__body", "Loading…");
    pop.appendChild(body);
    document.body.appendChild(pop);
    place(span);
    var mine = pop;
    Promise.all([T.data("forms.json"), T.data("lexicon.json")]).then(function (d) {
      if (pop !== mine) return;
      body.textContent = "";
      fill(body, token, d[0], d[1]);
      place(span);
    }).catch(function () {
      if (pop === mine) body.textContent = "The word list could not be loaded. Try again later.";
    });
  }

  document.addEventListener("click", function (ev) {
    var span = ev.target.closest && ev.target.closest(".th--click");
    if (span) { ev.preventDefault(); open(span); return; }
    if (pop && !pop.contains(ev.target)) close(false);
  });
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape" && pop) { close(true); return; }
    var span = ev.target.classList && ev.target.classList.contains("th--click") ? ev.target : null;
    if (span && (ev.key === "Enter" || ev.key === " ")) { ev.preventDefault(); open(span); }
  });
  window.addEventListener("resize", function () { if (pop && current) place(current); });

  // Exposed for testing
  T.analyze = function (token) {
    return Promise.all([T.data("forms.json"), T.data("lexicon.json")]).then(function (d) {
      var r = analyze(token, d[0]);
      return r.found.map(function (f) { return d[0].lemmas[f.lemma][0] + " " + f.tag + (f.poss ? " +" + f.poss : ""); });
    });
  };
})();
