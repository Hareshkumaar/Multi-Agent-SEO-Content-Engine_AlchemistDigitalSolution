// Generate page: submit the brief, read the SSE stream, move the progress timeline.
const form = $('#brief-form'), statusEl = $('#status'), topic = $('#topic');
const LABELS = JSON.parse($('[data-labels]').dataset.labels);
const step = (node) => $(`[data-step="${node}"]`);

topic.addEventListener('input', () => {
  const n = topic.value.trim().length;
  $('#topic-count').textContent = n;
  $('#topic-hint').textContent = n < 5 ? 'Use at least 5 characters.' : '';
});

function mark(node, state, note = '') {
  const el = step(node);
  if (!el) return;
  el.className = 'step ' + state;
  $('[data-note]', el).textContent = note;
}

function handle(ev) {
  if (ev.node === 'error') return fail(ev.message);
  if (ev.node === 'done') return (location.href = `/articles/${ev.article_id}/review`);
  if (ev.node !== 'start') mark(ev.node, 'is-done');
  if (ev.next && ev.next !== 'done') {
    const revising = ev.node === 'critic';      // the Critic sent the draft back once
    if (revising) { mark('critic', ''); statusEl.textContent = `Score ${ev.score}. Running one revision pass.`; }
    mark(ev.next, 'is-active', revising ? 'Revision pass' : '');
  }
}

function fail(message) {
  statusEl.textContent = 'Something failed: ' + message;
  statusEl.classList.add('over');
  $$('.field, #generate, .seg__btn').forEach((el) => (el.disabled = false));
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(form));
  if (data.topic.trim().length < 5) return topic.focus();
  data.reference_urls = (data.reference_urls || '').split('\n').map((s) => s.trim()).filter(Boolean);
  $$('.field, #generate, .seg__btn').forEach((el) => (el.disabled = true));
  statusEl.classList.remove('over');
  statusEl.textContent = 'Starting the pipeline.';
  try {
    const res = await fetch('/api/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    if (!res.ok) {
      const text = await res.text();
      let msg = text;
      try { const d = JSON.parse(text); msg = d.detail?.[0]?.msg || d.detail || text; } catch {}
      throw new Error(msg);
    }
    const reader = res.body.getReader(), dec = new TextDecoder();
    let buf = '';
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const parts = buf.split('\n\n');
      buf = parts.pop();
      parts.forEach((p) => handle(JSON.parse(p.replace(/^data: /, ''))));
    }
  } catch (err) { fail(err.message); }
});
