import { defineConfig } from 'vitest/config';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  plugins: [tsconfigPaths()],
  test: {
    environment: 'node',
    globals: true,
    include: ['src/**/__tests__/**/*.test.ts'],
    exclude: ['dist', 'node_modules'],
    reporters: ['default', ['json', { outputFile: 'vitest.json' }], ['html', { outputDir: 'vitest-html' }]],
    coverage: {
      reporter: ['text', 'html'],
    }
  },
});