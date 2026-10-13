/* Pure calculations shared by the browser UI and Node regression tests. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.TILScorer = api;
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';
  function calculate(stromalArea, occupiedArea) {
    const total = Number(stromalArea);
    const occupied = Number(occupiedArea);
    if (stromalArea === '' || occupiedArea === '' || stromalArea == null || occupiedArea == null ||
        !Number.isFinite(total) || !Number.isFinite(occupied)) {
      throw new Error('Both areas must be finite numbers.');
    }
    if (total <= 0) throw new Error('Eligible stromal area must be greater than zero.');
    if (occupied < 0) throw new Error('TIL-occupied area cannot be negative.');
    if (occupied > total) throw new Error('TIL-occupied area cannot exceed eligible stromal area.');
    return Math.round((occupied / total * 100 + Number.EPSILON) * 100) / 100;
  }
  function parseCSV(text) {
    if (typeof text !== 'string') throw new Error('Invalid CSV content.');
    const rows = [], row = [];
    let current = '', quoted = false, afterQuote = false;
    text = text.replace(/^\uFEFF/, '');
    for (let i = 0; i < text.length; i++) {
      const ch = text[i];
      if (quoted) {
        if (ch === '"' && text[i + 1] === '"') { current += '"'; i++; }
        else if (ch === '"') { quoted = false; afterQuote = true; }
        else current += ch;
      } else if (ch === '"') {
        if (current !== '' || afterQuote) throw new Error('Invalid CSV quoting.');
        quoted = true;
      } else if (ch === ',') {
        row.push(current); current = ''; afterQuote = false;
      } else if (ch === '\r' || ch === '\n') {
        if (ch === '\r' && text[i + 1] === '\n') i++;
        row.push(current);
        if (row.some(cell => cell !== '')) rows.push(row.slice());
        row.length = 0; current = ''; afterQuote = false;
      } else {
        if (afterQuote && ch !== ' ' && ch !== '\t') throw new Error('Invalid CSV quoting.');
        if (!afterQuote) current += ch;
      }
    }
    if (quoted) throw new Error('Unclosed quote in CSV.');
    row.push(current);
    if (row.some(cell => cell !== '')) rows.push(row);
    return rows;
  }
  function scoreCSV(text) {
    const rows = parseCSV(text);
    if (!rows.length) throw new Error('CSV file is empty.');
    const headers = rows[0].map(x => x.trim());
    if (new Set(headers).size !== headers.length) throw new Error('CSV column names must be unique.');
    const totalIndex = headers.indexOf('stromal_area');
    const tilIndex = headers.indexOf('til_area');
    if (totalIndex < 0 || tilIndex < 0) {
      throw new Error('CSV needs stromal_area and til_area columns.');
    }
    if (headers.includes('stromal_til_percent')) throw new Error('CSV already contains stromal_til_percent.');
    if (rows.length > 5001) throw new Error('CSV is limited to 5,000 cases.');
    const scored = rows.slice(1).map((row, index) => {
      if (row.length !== headers.length) throw new Error('Row ' + (index + 2) + ': incorrect column count.');
      try { return [...row, String(calculate(row[totalIndex], row[tilIndex]))]; }
      catch (e) { throw new Error('Row ' + (index + 2) + ': ' + e.message); }
    });
    return { headers: [...headers, 'stromal_til_percent'], rows: scored };
  }
  function encodeCSV(table) {
    const encodeCell = (cell, label) => {
      let value = String(cell);
      // Prevent spreadsheet formula execution when untrusted case labels are opened.
      if (label && /^[\s]*[=+\-@]/.test(value)) value = "'" + value;
      return '"' + value.replace(/"/g, '""') + '"';
    };
    return [table.headers.map(h => encodeCell(h, true)).join(','),
      ...table.rows.map(row => row.map((cell, i) => encodeCell(cell, i !== table.headers.length - 1)).join(','))
    ].join('\r\n') + '\r\n';
  }
  return { calculate, parseCSV, scoreCSV, encodeCSV };
});
