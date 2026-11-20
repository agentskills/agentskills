import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = await readFile(path.join(root, 'docs/snippets/clients.jsx'), 'utf8');
// The data module contains plain JavaScript, so it can be loaded without changing
// the package's module mode or executing the JSX rendering components.
const { clients } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);
const start = '{/* BEGIN GENERATED CLIENT DIRECTORY */}';
const end = '{/* END GENERATED CLIENT DIRECTORY */}';
const mdxPath = path.join(root, 'docs/clients.mdx');
const mdx = await readFile(mdxPath, 'utf8');
if (!mdx.includes(start) || !mdx.includes(end) || mdx.indexOf(start) >= mdx.indexOf(end)) throw new Error('Client directory markers missing or out of order');
const escapeText = value => value.replace(/[\\\[\]]/g, '\\$&');
const lines = [...clients].sort((a, b) => a.name.localeCompare(b.name, 'en')).map(({name, url}) => {
  if (typeof name !== 'string' || typeof url !== 'string' || !/^https?:\/\//.test(url) || /[\s()<>]/.test(url)) throw new Error(`Invalid client name or URL: ${name}`);
  return `- [${escapeText(name)}](<${url}>)`;
});
const next = mdx.slice(0, mdx.indexOf(start) + start.length) + '\n\n' + lines.join('\n') + '\n\n' + mdx.slice(mdx.indexOf(end));
if (process.argv.includes('--check')) {
  if (next !== mdx) { console.error('Client directory is out of date. Run node scripts/sync-client-markdown.mjs'); process.exitCode = 1; }
  else console.log(`Client directory is in sync (${clients.length} clients).`);
} else { await writeFile(mdxPath, next); console.log(`Updated client directory (${clients.length} clients).`); }
