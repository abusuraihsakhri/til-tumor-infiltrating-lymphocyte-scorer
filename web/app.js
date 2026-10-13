(function () {
  'use strict';
  const form = document.querySelector('#single-form');
  const result = document.querySelector('#result');
  const message = document.querySelector('#single-message');
  const batchMessage = document.querySelector('#batch-message');
  const fileInput = document.querySelector('#csv-file');
  const download = document.querySelector('#download');
  let processed = null;

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    message.textContent = '';
    result.textContent = '—';
    try {
      const total = form.elements.stromal_area.value;
      const occupied = form.elements.til_area.value;
      const percentage = TILScorer.calculate(total, occupied);
      result.textContent = percentage.toFixed(2) + '%';
      message.textContent = 'Continuous stromal TIL area fraction; no clinical tier is inferred.';
    } catch (err) { message.textContent = err.message; }
  });

  document.querySelector('#batch-form').addEventListener('submit', async function (event) {
    event.preventDefault();
    processed = null;
    download.disabled = true;
    batchMessage.textContent = '';
    const file = fileInput.files[0];
    if (!file) { batchMessage.textContent = 'Select a CSV file.'; return; }
    if (file.size > 2 * 1024 * 1024) {
      batchMessage.textContent = 'File exceeds the 2 MB limit.'; return;
    }
    try {
      processed = TILScorer.scoreCSV(await file.text());
      batchMessage.textContent = processed.rows.length + ' cases validated. Ready to export.';
      download.disabled = false;
    } catch (err) { batchMessage.textContent = err.message; }
  });

  download.addEventListener('click', function () {
    if (!processed) return;
    const blob = new Blob([TILScorer.encodeCSV(processed)], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'stromal-til-results.csv';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  });
  fileInput.addEventListener('change', function () {
    processed = null;
    download.disabled = true;
    batchMessage.textContent = '';
  });
})();
