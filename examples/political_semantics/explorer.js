/* Offline UI: corpus text is always inserted as text, never interpreted as HTML. */
(() => {
  'use strict';
  const payload = JSON.parse(document.getElementById('dataset').textContent);
  const data = payload.corpus;
  const sourceById = new Map(data.sources.map(row => [row.id, row]));
  const evidenceById = new Map(data.evidence.map(row => [row.id, row]));
  const actorById = new Map(data.actors.map(row => [row.id, row]));
  const labels = {policy_analysis: 'Policy analysis', mediation: 'Mediation', media_narrative: 'Media & narrative', hr_policy: 'HR policy'};
  const checked = new Set(['source_verified', 'human_reviewed']);
  let lens = 'mediation';
  let selection;
  const byId = id => document.getElementById(id);
  const element = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const words = value => String(value).replaceAll('_', ' ');
  const label = id => actorById.get(id)?.label || id || 'Not specified';
  const purpose = value => typeof value === 'string' ? value : value.description || value.purpose || JSON.stringify(value);
  const addField = (dl, name, value) => {
    dl.append(element('dt', name), element('dd', value === null || value === undefined || value === '' ? 'Not assessed / not specified' : String(value)));
  };

  function selectRows() {
    const drafts = byId('drafts').checked;
    const cutoff = byId('published-by').value;
    const rows = data.records.filter(row => {
      if (!row.lenses.includes(lens) || (!drafts && !checked.has(row.review_state))) return false;
      return !cutoff || row.evidence.every(link => {
        const source = sourceById.get(evidenceById.get(link.evidence_id).source_id);
        const published = source.published.value + (source.published.precision === 'year' ? '-12-31' : '');
        return published <= cutoff;
      });
    }).sort((a, b) => a.id.localeCompare(b.id));
    const evidenceIds = new Set(rows.flatMap(row => row.evidence.map(link => link.evidence_id)));
    const evidence = data.evidence.filter(row => evidenceIds.has(row.id));
    const sourceIds = new Set(evidence.map(row => row.source_id));
    return {format: 'political-lens-selection/1', lens, published_by: cutoff || null, include_drafts: drafts,
      selection_method: 'explicit lens tags and review states; no relevance or bias scoring',
      records: rows, evidence, sources: data.sources.filter(row => sourceIds.has(row.id)), limits: data.limits};
  }

  function recordCard(row) {
    const article = element('article');
    const meta = element('div', undefined, 'record-meta');
    meta.append(element('span', row.primitive), element('span', row.id));
    meta.append(element('span', row.review_state === 'source_verified' ? 'Source wording checked' : words(row.review_state), checked.has(row.review_state) ? '' : 'draft'));
    article.append(meta, element('h3', row.statement));
    const dl = element('dl');
    addField(dl, 'Attributed to', label(row.attributed_to));
    addField(dl, 'Reported by', row.reported_by ? label(row.reported_by) : 'Direct source / no separate reporter');
    addField(dl, 'Basis', words(row.basis));
    addField(dl, 'Text / action', words(row.document_stage) + ' · ' + row.modality);
    addField(dl, 'Implementation', words(row.implementation));
    addField(dl, 'Occurrence', row.time.occurred_on);
    addField(dl, 'Validity', row.time.validity_status === 'not_assessed' ? 'Not assessed' : `${row.time.valid_from || '?'} → ${row.time.valid_to || '?'}`);
    addField(dl, 'Authority / scope', `${row.authority} · ${row.scope}`);
    addField(dl, 'Human approval', row.human_reviewed ? 'Review metadata supplied; identity not authenticated by this demo' : 'None');
    article.append(dl);
    const disclosure = element('details');
    disclosure.append(element('summary', `Inspect ${row.evidence.length} source passage${row.evidence.length === 1 ? '' : 's'}`));
    for (const link of row.evidence) {
      const evidence = evidenceById.get(link.evidence_id);
      const source = sourceById.get(evidence.source_id);
      const box = element('div', undefined, 'evidence-item');
      const title = element('a', source.title, 'source-title');
      try {
        const url = new URL(source.url);
        if (url.protocol === 'https:') { title.href = url.href; title.target = '_blank'; title.rel = 'noopener noreferrer'; }
      } catch { /* Retain the visible title when a future source URL is malformed. */ }
      box.append(title, element('p', `${source.document_symbol || source.genre} · published ${source.published.value} · publisher: ${label(source.publisher_id)}`, 'source-meta'));
      box.append(element('blockquote', link.quote), element('p', evidence.locator, 'source-meta'));
      box.append(element('p', `Retained excerpt SHA-256: ${evidence.retained_sha256}`, 'digest'));
      if (source.original_sha256) box.append(element('p', `Consulted PDF SHA-256: ${source.original_sha256}`, 'digest'));
      box.append(element('p', `Recorded ${evidence.recorded_at || source.recorded_at}. Hashes check representation bytes; they do not certify the assertion.`, 'source-meta'));
      disclosure.append(box);
    }
    article.append(disclosure);
    return article;
  }

  function renderRecipe() {
    const target = byId('recipe-detail');
    target.replaceChildren();
    const recipe = data.recipes[byId('recipe').value];
    if (!recipe) return;
    const box = element('div', undefined, 'recipe-box');
    box.append(element('h3', words(byId('recipe').value)), element('p', 'Review questions for this task:'));
    const list = element('ul');
    for (const question of recipe.review_questions) list.append(element('li', question));
    box.append(list);
    target.append(box);
  }

  function render() {
    selection = selectRows();
    byId('results-title').textContent = labels[lens] || words(lens);
    byId('purpose').textContent = purpose(data.lenses[lens]);
    byId('count').textContent = `${selection.records.length} records · ${selection.sources.length} sources`;
    const nodes = selection.records.map(recordCard);
    if (!nodes.length) nodes.push(element('p', 'No records meet these filters. Change the publication cutoff or explicitly include drafts; absence here is not absence in the world.', 'empty'));
    byId('record-list').replaceChildren(...nodes);
    for (const button of byId('lenses').querySelectorAll('button')) button.setAttribute('aria-pressed', String(button.dataset.lens === lens));
    renderRecipe();
  }

  function download(name, value, type) {
    const text = typeof value === 'string' ? value : JSON.stringify(value, null, 2) + '\n';
    const url = URL.createObjectURL(new Blob([text], {type}));
    const anchor = element('a'); anchor.href = url; anchor.download = name;
    document.body.append(anchor); anchor.click(); anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  for (const key of Object.keys(data.lenses)) {
    const count = data.records.filter(row => row.lenses.includes(key) && checked.has(row.review_state)).length;
    const button = element('button'); button.type = 'button'; button.dataset.lens = key;
    button.append(element('span', labels[key] || words(key)), element('small', `${count} checked`));
    button.addEventListener('click', () => { lens = key; byId('recipe').value = ''; render(); });
    byId('lenses').append(button);
  }
  for (const [key, recipe] of Object.entries(data.recipes)) {
    const option = element('option', words(key)); option.value = key; byId('recipe').append(option);
  }
  byId('recipe').addEventListener('change', () => { if (data.recipes[byId('recipe').value]) lens = data.recipes[byId('recipe').value].lens; render(); });
  byId('drafts').addEventListener('change', render);
  byId('published-by').addEventListener('change', render);
  byId('selection').addEventListener('click', () => download(`tacitus-${lens}-selection.json`, selection, 'application/json'));
  byId('jsonld').addEventListener('click', () => download('tacitus-political-demo.jsonld', payload.jsonld, 'application/ld+json'));
  byId('sql').addEventListener('click', () => download('tacitus-political-demo.sql', payload.sql, 'application/sql'));
  render();
})();
