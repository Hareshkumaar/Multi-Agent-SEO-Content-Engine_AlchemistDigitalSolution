// Editor page: live preview, character counters, live SEO snapshot, save edits.
const root = $('#article'), d = root.dataset, id = d.id;
const md = $('#md'), mt = $('#meta_title'), mdsc = $('#meta_description');
const render = () => ($('#preview').innerHTML = DOMPurify.sanitize(marked.parse(md.value)));

function snapshot() {
  const words = md.value.trim().split(/\s+/).filter(Boolean);
  const kw = d.kw.toLowerCase();
  const h1 = (md.value.split(/\r?\n/).find((l) => l.startsWith('# ')) || '').toLowerCase();
  const first = words.slice(0, +d.firstWords).join(' ').toLowerCase();
  const checks = [
    [`Words: ${words.length}/${d.minWords}`, words.length >= +d.minWords],
    ['Keyword in H1', !!kw && h1.includes(kw)],
    [`Keyword in first ${d.firstWords} words`, !!kw && first.includes(kw)],
    [`Title: ${mt.value.length}/${d.titleMax}`, mt.value.length <= +d.titleMax],
    [`Description: ${mdsc.value.length}/${d.descMax}`, mdsc.value.length <= +d.descMax],
  ];
  $('#snapshot').innerHTML = checks.map(([label, ok]) =>
    `<span class="pill pill--${ok ? 'green' : 'red'}">${label}</span>`
  ).join('');
}

[md, mt, mdsc].forEach((el) => el.addEventListener('input', snapshot));
md.addEventListener('input', render);
render();
snapshot();

$$('[data-count]').forEach((el) => {
  const out = $(el.dataset.count);
  const update = () => { out.textContent = `${el.value.length}/${el.maxLength}`; out.classList.toggle('over', el.value.length >= el.maxLength); };
  el.addEventListener('input', update);
  update();
});

async function save() {
  const body = {};
  $$('[data-field]').forEach((el) => (body[el.dataset.field] = el.value));
  await api(`/api/articles/${id}`, { method: 'PUT', body: JSON.stringify(body) });
}
window.saveEdits = save;

$('#save').addEventListener('click', async () => {
  try { await save(); toast('Saved'); } catch (e) { toast(e.message); }
});
