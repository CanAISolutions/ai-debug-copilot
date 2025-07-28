/**
 * Minimal type declarations for the VS Code API used by this extension.
 *
 * This shim avoids the need for the full @types/vscode package, which cannot
 * be installed in the current environment due to network restrictions. The
 * declarations here are intentionally loose (using `any`) to satisfy the
 * TypeScript compiler while still allowing the extension to compile.
 */
declare module 'vscode' {
  export const commands: any;
  export const window: any;
  export const workspace: any;
  export const ViewColumn: any;
  export interface Webview {
    postMessage: any;
    onDidReceiveMessage: any;
    html: string;
  }
  export interface Uri {}
  export interface WebviewPanel {
    webview: any;
  }
  export interface ExtensionContext {
    extensionUri: any;
    subscriptions: any[];
  }
}