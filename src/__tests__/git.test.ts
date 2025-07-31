import { describe, it, expect, vi } from 'vitest';

// Mock child_process before importing the module
vi.mock('child_process', () => ({
  execSync: () => Buffer.from('foo.ts\nbar.js\n')
}));

vi.mock('vscode', () => ({ default: {} }));

import { getChangedFiles } from '../extension';

describe('getChangedFiles()', () => {
  it('returns list from git diff', () => {
    const files = getChangedFiles(process.cwd());
    expect(files).toEqual(['foo.ts', 'bar.js']);
  });
});