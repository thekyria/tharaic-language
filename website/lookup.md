# English → Tharaic lookup

Type English and press **Look up**. Each English word is replaced by a Tharaic word from the [lexicon](lexicon.md); the table below the result gives its meaning and the other words you could use instead. The *Script* and *Font* buttons at the top of the page change how the Tharaic is shown.

!!! note "A word-by-word lookup, not a translation"
    The result keeps the English word order and gives each word in its dictionary form (nouns in the nominative singular, verbs in the infinitive). Real Tharaic puts the verb first and marks the role of each noun with a case ending: see [Syntax](syntax.md) and [Morphology](morphology.md). Words that are not in the lexicon are shown in [brackets].

<div class="th-lookup" id="th-lookup" markdown="0">
  <label for="th-lookup-input" class="th-lookup__hint">English text</label>
  <textarea id="th-lookup-input" rows="4" placeholder="The sailor sails the ship to the harbor.">The sailor sails the ship to the harbor.</textarea>
  <div class="th-lookup__bar">
    <button type="button" class="th-lookup__go" id="th-lookup-go">Look up</button>
    <span class="th-controls__group" role="radiogroup" aria-label="Register">
      <span class="th-controls__label">Prefer</span>
      <button type="button" data-th-register="everyday" aria-pressed="true">everyday words</button>
      <button type="button" data-th-register="high" aria-pressed="false">high-register words</button>
    </span>
    <button type="button" id="th-lookup-copy">Copy result</button>
    <span class="th-lookup__hint">Ctrl+Enter also looks up</span>
  </div>
  <div class="th-lookup__output" id="th-lookup-output" aria-live="polite"></div>
  <div id="th-lookup-detail"></div>
</div>
