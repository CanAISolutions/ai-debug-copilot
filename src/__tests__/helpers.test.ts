import { describe, expect, it, vi } from 'vitest';
import pako from 'pako';

// Mock the vscode module before importing extension
vi.mock('vscode', () => ({
  default: {},
}));

import { gzipBase64 } from '../extension';

function decode(b64: string): string {
  const buf = Buffer.from(b64, 'base64');
  const raw = pako.ungzip(buf);
  return Buffer.from(raw).toString('utf-8');
}

describe('gzipBase64()', () => {
  it('round-trips small content', () => {
    const text = 'hello AI debug';
    const encoded = gzipBase64(Buffer.from(text, 'utf-8'));
    expect(decode(encoded)).toBe(text);
  });
});