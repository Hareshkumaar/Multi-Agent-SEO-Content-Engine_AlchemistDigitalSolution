// Status transition buttons on Review and Editor pages.
function confirmApprove(low, pass) {
  const dlg = $('#confirm-dialog');
  if (!dlg) return Promise.resolve(true);
  const badge = $('#confirm-badge'), msg = $('#confirm-msg');
  badge.textContent = `Critic score below ${pass}`;
  badge.hidden = !low;
  msg.textContent = low
    ? 'The Critic flagged issues below the quality bar. Approve anyway, or cancel to edit first.'
    : 'Confirm you have reviewed the article and Critic feedback.';
  dlg.showModal();
  return new Promise((resolve) => {
    const done = (ok) => { dlg.close(); resolve(ok); };
    $('#confirm-ok').onclick = () => done(true);
    $('#confirm-cancel').onclick = () => done(false);
    dlg.oncancel = (e) => { e.preventDefault(); done(false); };
    dlg.onclick = (e) => { if (e.target === dlg) done(false); };
  });
}

$$('[data-status]').forEach((btn) => btn.addEventListener('click', async () => {
  const { id, score, pass } = $('#article').dataset, status = btn.dataset.status;
  if (status === 'approved' && !(await confirmApprove(score !== '' && +score < +pass, pass))) return;
  try {
    if (window.saveEdits) await window.saveEdits();
    await api(`/api/articles/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) });
    location.reload();
  } catch (e) { toast(e.message); }
}));
