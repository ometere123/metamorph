// Pure preflight: never silently switch to the CLI's dev/next preset.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const root = path.resolve(import.meta.dirname, '..');
const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
if (pkg.devDependencies?.genlayer !== '0.39.1') {
  throw new Error('Repository CLI must be pinned to exactly genlayer@0.39.1');
}
const config = JSON.parse(fs.readFileSync(path.join(root, 'network.json'), 'utf8'));
if (config.network !== 'studionet' || config.chainId !== 61999 || config.rpc !== 'https://studio.genlayer.com/api') {
  throw new Error('Network guard: only studionet / 61999 is allowed');
}
const all = JSON.stringify(config).toLowerCase();
if (all.includes('studio-dev') || all.includes('61997')) throw new Error('Dev network found');
const testConfig = fs.readFileSync(path.join(root, 'gltest.config.yaml'), 'utf8');
if (!/default:\s*studionet\b/.test(testConfig) || !testConfig.includes(config.rpc)) {
  throw new Error('GenLayer test configuration must target studionet 61999');
}
const binaryCandidates = process.platform === 'win32'
  ? [path.join(root, 'node_modules', '.bin', 'genlayer.cmd'),
     path.join(root, 'node_modules', '.bin', 'genlayer')]
  : [path.join(root, 'node_modules', '.bin', 'genlayer')];
const binary = binaryCandidates.find((candidate) => fs.existsSync(candidate));
if (!binary) throw new Error('Repository-local GenLayer CLI executable not found');
const spawnOptions = { encoding: 'utf8', ...(process.platform === 'win32' ? { shell: true } : {}) };
const version = execFileSync(binary, ['--version'], spawnOptions).trim();
if (version !== '0.39.1') throw new Error(`Wrong local CLI: ${version}`);
const selected = execFileSync(binary, ['network', 'info'], spawnOptions);
if (!selected.includes("alias: 'studionet'") || !selected.includes("chainId: '61999'") ||
    !selected.includes(`rpc: '${config.rpc}'`)) {
  throw new Error('Selected CLI network is not stable studionet 61999');
}
console.log('PASS: studionet / chain 61999 / local GenLayer CLI 0.39.1');
