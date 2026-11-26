const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

async function api(path, opts = {}) {
  const res = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...opts });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(Array.isArray(data.detail) ? data.detail[0].msg : data.detail || res.statusText);
  return data;
}

function toast(msg) {
  const t = $('#toast');
  t.textContent = msg; t.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => (t.hidden = true), 2500);
}

document.addEventListener('click', (e) => {
  const btn = e.target.closest('.seg__btn');
  if (!btn) return;
  const seg = btn.closest('.seg');
  seg.querySelectorAll('.seg__btn').forEach((b) => b.classList.toggle('is-active', b === btn));
  if (seg.dataset.target) $(seg.dataset.target).value = btn.dataset.value;
});

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const bell = $('#bell'), menu = $('#notif-menu');
if (bell && menu) {
  let cached = null;
  const close = () => { menu.hidden = true; bell.setAttribute('aria-expanded', 'false'); };
  bell.addEventListener('click', async (e) => {
    e.stopPropagation();
    if (!menu.hidden) return close();
    menu.hidden = false;
    bell.setAttribute('aria-expanded', 'true');
    if (!cached) menu.innerHTML = '<p class="sub">Loading...</p>';
    try {
      cached = cached || await api('/api/articles');
      const items = cached.slice(0, 5);
      menu.innerHTML = `<div class="stack"><div class="card__title" style="margin:0">Recent articles</div>${
        items.length ? items.map((a) => `<a class="item" href="/articles/${a.id}/review">
          <div class="item__body"><div class="item__title clamp-1">${esc(a.topic)}</div>
          <div class="item__sub">${esc(a.status)}${a.quality_score != null ? ' · Score ' + a.quality_score : ''}</div></div></a>`).join('')
        : '<p class="sub">No recent articles yet.</p>'
      }</div>`;
    } catch (err) { menu.innerHTML = `<p class="sub">${esc(err.message)}</p>`; }
  });
  document.addEventListener('click', (e) => { if (!menu.hidden && !e.target.closest('.notif-wrap')) close(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !menu.hidden) close(); });
}
