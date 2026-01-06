import { DynamicStructuredTool } from '@langchain/core/tools';
import { z } from 'zod';
import fs from 'fs';
import path from 'path';
import { formatToolResult } from '../types.js';

type Row = Record<string, string>;

function findReportsDirs(baseCwd: string): string[] {
  // Prefer top-level reports/, fallback to polymarket-research/reports/
  const candidates = [
    path.resolve(baseCwd, '..', 'reports'),
    path.resolve(baseCwd, '..', 'polymarket-research', 'reports'),
  ];
  return candidates.filter((p) => fs.existsSync(p) && fs.statSync(p).isDirectory());
}

function listMatchingCsvFiles(dir: string, kind: 'top24h' | 'all'): string[] {
  const entries = fs.readdirSync(dir);
  const matcher = kind === 'top24h'
    ? /^top_markets_24h_.*\.csv(?:\.gz)?$/
    : /^all_active_markets_.*\.csv(?:\.gz)?$/;
  return entries.filter((f) => matcher.test(f)).map((f) => path.join(dir, f));
}

function getLatestFile(paths: string[]): string | null {
  if (paths.length === 0) return null;
  const withTimes = paths.map((p) => ({ p, t: fs.statSync(p).mtimeMs }));
  withTimes.sort((a, b) => b.t - a.t);
  return withTimes[0].p;
}

// Minimal RFC4180 CSV parser supporting quotes and commas within quotes
function parseCsv(content: string): Row[] {
  const rows: string[][] = [];
  let current: string[] = [];
  let field = '';
  let inQuotes = false;
  let i = 0;
  while (i < content.length) {
    const ch = content[i];
    if (inQuotes) {
      if (ch === '"') {
        if (i + 1 < content.length && content[i + 1] === '"') {
          field += '"';
          i += 2;
          continue;
        } else {
          inQuotes = false;
          i++;
          continue;
        }
      } else {
        field += ch;
        i++;
        continue;
      }
    } else {
      if (ch === '"') {
        inQuotes = true;
        i++;
        continue;
      }
      if (ch === ',') {
        current.push(field);
        field = '';
        i++;
        continue;
      }
      if (ch === '\n' || ch === '\r') {
        // Handle CRLF or LF
        // finalize row only if we have data or first field encountered
        // Consume optional LF after CR
        if (ch === '\r' && i + 1 < content.length && content[i + 1] === '\n') {
          i += 2;
        } else {
          i++;
        }
        current.push(field);
        field = '';
        // ignore empty last line
        if (current.some((x) => x !== '')) {
          rows.push(current);
        }
        current = [];
        continue;
      }
      field += ch;
      i++;
    }
  }
  // flush last field/row
  if (inQuotes) {
    // Unbalanced quotes; attempt to flush
  }
  current.push(field);
  if (current.length > 1 || (current.length === 1 && current[0] !== '')) {
    rows.push(current);
  }
  if (rows.length === 0) return [];
  const header = rows[0];
  return rows.slice(1).map((r) => {
    const obj: Row = {};
    for (let idx = 0; idx < header.length; idx++) {
      obj[header[idx]] = r[idx] ?? '';
    }
    return obj;
  });
}

function safeJsonParse<T>(text: string): T | null {
  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
}

export const loadPolymarketReports = new DynamicStructuredTool({
  name: 'polymarket_reports',
  description:
    'Load latest Polymarket CSV report from local reports folder and return parsed rows. Useful for summarizing top markets or all active markets without calling external APIs.',
  schema: z.object({
    kind: z
      .enum(['top24h', 'all'])
      .describe("Which report to load: 'top24h' or 'all' (active markets)"),
    limit: z
      .number()
      .int()
      .positive()
      .optional()
      .describe('Optional maximum number of rows to return'),
  }),
  func: async ({ kind, limit }: { kind: 'top24h' | 'all'; limit?: number }) => {
    const cwd = process.cwd();
    const dirs = findReportsDirs(cwd);
    if (dirs.length === 0) {
      return formatToolResult({
        error: 'No reports directory found. Expected reports/ or polymarket-research/reports/.',
      });
    }
    // gather files across dirs and pick the latest overall
    const files = dirs.flatMap((d) => listMatchingCsvFiles(d, kind));
    const latest = getLatestFile(files);
    if (!latest) {
      return formatToolResult({ error: `No ${kind} report files found in ${dirs.join(', ')}` });
    }
    const csv = fs.readFileSync(latest, 'utf8');
    const rows = parseCsv(csv);

    // Map and enrich some fields if present
    const mapped = rows.map((r) => {
      const outcomes = safeJsonParse<string[]>(r['outcomes'] || '') || undefined;
      const outcomePrices = safeJsonParse<string[]>(r['outcomePrices'] || '') || undefined;
      let impliedYesProb: number | undefined;
      if (outcomes && outcomePrices && outcomes.length === outcomePrices.length) {
        const yesIndex = outcomes.findIndex((o) => o.toLowerCase() === 'yes');
        if (yesIndex >= 0) {
          const p = Number(outcomePrices[yesIndex]);
          if (!Number.isNaN(p)) impliedYesProb = p;
        }
      }
      return {
        snapshot_time: r['snapshot_time'] || r['asOf'] || undefined,
        question: r['question'] || r['title'] || undefined,
        slug: r['slug'] || undefined,
        category: r['category'] || undefined,
        endDate: r['endDate'] || undefined,
        volume24hr: r['volume24hr'] ? Number(r['volume24hr']) : undefined,
        volume_total: r['volume_total'] ? Number(r['volume_total']) : undefined,
        liquidity: r['liquidity'] ? Number(r['liquidity']) : undefined,
        outcomes,
        outcomePrices: outcomePrices?.map((x) => Number(x)),
        impliedYesProb,
      };
    });

    const limited = typeof limit === 'number' ? mapped.slice(0, limit) : mapped;
    return formatToolResult({
      kind,
      file: latest,
      count: limited.length,
      rows: limited,
    }, []);
  },
});

export default loadPolymarketReports;
