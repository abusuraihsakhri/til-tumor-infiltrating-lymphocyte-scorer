const test = require('node:test');
const assert = require('node:assert/strict');
const { calculate, parseCSV, scoreCSV, encodeCSV } = require('../web/scorer.js');

test('continuous area percentage and boundaries', () => {
  assert.equal(calculate(200, 50), 25);
  assert.equal(calculate(3, 1), 33.33);
  assert.equal(calculate(100, 0), 0);
  assert.equal(calculate(100, 100), 100);
});
test('rejects invalid ratios and non-finite values', () => {
  for (const pair of [[0, 0], [10, -1], [10, 11], ['no', 1], ['', ''], [Infinity, 2]]) {
    assert.throws(() => calculate(...pair));
  }
});
test('parses escaped commas/newlines and produces valid results', () => {
  const table = scoreCSV('\uFEFFsample_id,stromal_area,til_area\r\n"Case, 1",200,50\r\n"Line\ntwo",80,0\r\n');
  assert.equal(table.rows.length, 2);
  assert.equal(table.rows[0][0], 'Case, 1');
  assert.equal(table.rows[0][3], '25');
  assert.equal(parseCSV(encodeCSV(table))[2][0], 'Line\ntwo');
});
test('CSV errors identify the row and reject extra fields', () => {
  assert.throws(() => scoreCSV('stromal_area,til_area\n10,15'), /Row 2/);
  assert.throws(() => scoreCSV('stromal_area,til_area\n10,5,extra'), /column count/);
  assert.throws(() => scoreCSV('v1,v2\n10,5'), /needs/);
  assert.throws(() => parseCSV('"unclosed'), /Unclosed/);
});
test('export prevents spreadsheet formula injection in labels', () => {
  const csv = encodeCSV(scoreCSV('sample_id,stromal_area,til_area\n=1+1,10,2'));
  assert.ok(csv.includes('"\'=1+1"'));
});
