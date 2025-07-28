/**
 * Minimal declaration for the `pako` module. Declares the exported gzip function
 * as `any` to satisfy TypeScript when type definitions are unavailable.
 */
declare module 'pako' {
  const gzip: any;
  export default {
    gzip,
  };
}