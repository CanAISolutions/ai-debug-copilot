#!/usr/bin/env node
// Collect failing Vitest (or Jest) test cases and emit JSON summary.
// Currently supports Vitest JSON reporter.
// Usage:  node scripts/collect-failing-tests.js
// Requires vitest to be in project devDependencies.

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

function detectTestCommand() {
  const pkgPath = path.resolve('package.json');
  if (!fs.existsSync(pkgPath)) throw new Error('package.json not found');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  // Prefer yarn/npm test script if includes vitest
  const testScript = pkg.scripts?.test ?? '';
  if (testScript.includes('vitest')) return `${testScript} --reporter=json --outputFile=vitest.json`;
  // fallback
  return 'npx vitest run --reporter=json --outputFile=vitest.json';
}

function runTests(cmd) {
  console.log('[collect] running:', cmd);
  try {
    execSync(cmd, { stdio: 'inherit', shell: true });
  } catch {
    // test failures exit non-zero; ignore
  }
}

function parseVitest() {
  const reportPath = path.resolve('vitest.json');
  if (!fs.existsSync(reportPath)) return { failures: [] };
  const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
  const failures = [];
  for (const file of report.testResults ?? []) {
    for (const test of file.assertionResults ?? []) {
      if (test.status === 'failed') {
        failures.push({
          title: test.fullName,
          file: file.name,
          failureMessages: test.failureMessages,
        });
      }
    }
  }
  return { failures };
}

function main() {
  const cmd = detectTestCommand();
  runTests(cmd);
  const result = parseVitest();
  console.log(JSON.stringify(result, null, 2));
}

main();
