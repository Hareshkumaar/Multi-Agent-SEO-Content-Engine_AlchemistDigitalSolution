// Status transition buttons on Review and Editor pages.
$$('[data-status]').forEach((btn) => btn.addEventListener('click', async () => {
  const { id, score, pass } = $('#article').dataset, status = btn.dataset.status;
  if (status === 'approved') {
    const warn = score !== '' && +score < +pass ? '\n\nWarning: the Critic score is below ' + pass + '.' : '';
    if (!confirm('Have you read the article and the Critic feedback?' + warn)) return;
  }
  try {
    if (window.saveEdits) await window.saveEdits();
    await api(`/api/articles/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) });
    location.reload();
  } catch (e) { toast(e.message); }
}));
