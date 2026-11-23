import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const methods = [
  ['stratified', 'Census-weighted Vertex pretest'],
  ['single', 'One national Vertex call'],
  ['previous', 'Previous human survey (2022)'],
];

function requireDistribution(shares) {
  if (!Array.isArray(shares) || shares.length !== 3 || shares.some(p => !Number.isFinite(p) || p < 0 || p > 1) ||
      Math.abs(shares.reduce((sum, share) => sum + share, 0) - 1) > 1e-8) {
    throw new Error('Expected a substantive three-option distribution.');
  }
}

export function scoreUSBenchmark(rows) {
  if (!Array.isArray(rows) || !rows.length || new Set(rows.map(row => row.id)).size !== rows.length) throw new Error('Expected unique, covered questions.');
  const items = rows.map(row => {
    requireDistribution(row.target.shares);
    const errors = Object.fromEntries(methods.map(([method]) => {
      const forecast = method === 'previous' ? row.previous.shares : row[method];
      requireDistribution(forecast);
      const target = row.target.shares;
      const totalVariation = forecast.reduce((sum, p, i) => sum + Math.abs(p - target[i]), 0) / 2;
      const brier = (1 + forecast.reduce((sum, p, i) => sum + p * p - 2 * p * target[i], 0)) / 2;
      return [method, { totalVariation, brier }];
    }));
    return { id: row.id, errors };
  });
  const summary = Object.fromEntries(methods.map(([method]) => [method, {
    meanTotalVariation: items.reduce((sum, item) => sum + item.errors[method].totalVariation, 0) / items.length,
    meanBrier: items.reduce((sum, item) => sum + item.errors[method].brier, 0) / items.length,
  }]));
  return { items, summary };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [action, first] = process.argv.slice(2);
  if (action === 'verify' && first) {
    const data = JSON.parse(readFileSync(first, 'utf8'));
    const recomputed = scoreUSBenchmark(data.rows);
    if (JSON.stringify(recomputed) !== JSON.stringify(data.scores)) throw new Error('Stored scores do not match the reported item distributions.');
    console.log(JSON.stringify(recomputed.summary, null, 2));
  } else throw new Error('Use verify PUBLIC_ARTIFACT.');
}
