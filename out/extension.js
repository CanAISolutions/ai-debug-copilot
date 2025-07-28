"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const cp = __importStar(require("child_process"));
const pako_1 = __importDefault(require("pako"));
// Simple in‑memory store for sessions. Keys are timestamps.
const sessions = {};
// Track the last payload sent to the backend so follow‑up answers can be appended.
let lastPayload = null;
// Track the number of follow‑up cycles. This is managed in the webview but
// maintained here to determine when to stop auto follow‑ups if desired.
let followUpCount = 0;
/**
 * Get the default list of changed files using git. Falls back to empty list.
 * @param workspaceRoot root of the workspace
 */
function getChangedFiles(workspaceRoot) {
    try {
        // Get names of changed files since HEAD. Trim to remove trailing newline.
        const output = cp.execSync('git diff --name-only HEAD', { cwd: workspaceRoot }).toString().trim();
        if (!output) {
            return [];
        }
        return output.split(/\r?\n/).filter(Boolean);
    }
    catch (err) {
        console.error('Error while obtaining git diff:', err);
        return [];
    }
}
/**
 * Compress file contents with gzip and encode to base64.
 * @param data Buffer of file contents
 */
function gzipBase64(data) {
    const compressed = pako_1.default.gzip(data);
    // Convert Uint8Array to Buffer for base64 conversion
    const buf = Buffer.from(compressed);
    return buf.toString('base64');
}
/**
 * Build the HTML for the WebView. Embeds the list of default files as JSON for the script.
 * @param webview The webview used to convert URIs for local resources
 * @param extensionUri The extension URI for resolving resources
 * @param changedFiles List of changed files to preselect
 */
function getWebviewContent(webview, extensionUri, changedFiles) {
    // Create the base HTML for the UI. Includes styling and simple form controls.
    const escapedFilesJson = JSON.stringify(changedFiles);
    return `<!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline';">
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Debugging Copilot</title>
    <style>
      body { font-family: sans-serif; padding: 16px; }
      h2 { margin-bottom: 1rem; }
      select { width: 100%; }
      textarea { width: 100%; min-height: 100px; margin-bottom: 1rem; }
      button { margin-top: 0.5rem; padding: 0.5rem 1rem; }
      .banner { display: none; padding: 0.5rem; margin-bottom: 1rem; border-radius: 4px; background-color: #fffae6; border: 1px solid #ffd42a; font-weight: bold; }
      .diff-viewer { font-family: monospace; border: 1px solid #ddd; padding: 0.5rem; margin-top: 0.5rem; overflow-x: auto; white-space: pre; }
      .diff-line.added { color: green; }
      .diff-line.removed { color: red; }
      .diff-line.header { color: purple; font-weight: bold; }
      #patchesContainer { margin-top: 1rem; }
      #followUpContainer { margin-top: 1rem; }
      #followUpContainer textarea { height: 60px; }
      #followUpContainer button { margin-right: 0.5rem; }
    </style>
  </head>
  <body>
    <h2>AI Debugging Copilot</h2>
    <!-- Root cause banner -->
    <div id="rootCauseBanner" class="banner"></div>
    <div>
      <label for="fileSelect"><strong>Changed files</strong> (select files to include):</label><br/>
      <select id="fileSelect" multiple size="8"></select>
    </div>
    <div>
      <label for="errorLog"><strong>Error log</strong> (paste failing test output):</label><br/>
      <textarea id="errorLog" placeholder="Paste your error log here..."></textarea>
    </div>
    <div>
      <label for="summary"><strong>Recent changes summary</strong> (describe what you changed):</label><br/>
      <textarea id="summary" placeholder="Briefly describe recent changes..."></textarea>
    </div>
    <button id="diagnoseButton">Diagnose</button>
    <!-- Container for patches/diffs -->
    <div id="patchesContainer"></div>
    <!-- Follow-up question container -->
    <div id="followUpContainer" style="display:none;">
      <p id="followUpQuestion" style="font-weight:bold;"></p>
      <textarea id="followUpAnswer" placeholder="Your answer..."></textarea><br/>
      <button id="submitFollowUp">Submit</button>
      <button id="escalateButton" style="display:none;">Escalate</button>
    </div>
    <script>
      (function() {
        const vscode = acquireVsCodeApi();
        const defaultFiles = ${escapedFilesJson};
        const select = document.getElementById('fileSelect');
        const rootBanner = document.getElementById('rootCauseBanner');
        const patchesContainer = document.getElementById('patchesContainer');
        const followUpContainer = document.getElementById('followUpContainer');
        const followUpQuestion = document.getElementById('followUpQuestion');
        const followUpAnswer = document.getElementById('followUpAnswer');
        const submitFollowUp = document.getElementById('submitFollowUp');
        const escalButton = document.getElementById('escalateButton');
        let followUpCount = 0;
        // Populate select with default files
        defaultFiles.forEach(file => {
          const option = document.createElement('option');
          option.value = file;
          option.textContent = file;
          option.selected = true;
          select.appendChild(option);
        });
        // Handle diagnose button click
        document.getElementById('diagnoseButton').addEventListener('click', () => {
          const selectedFiles = Array.from(select.selectedOptions).map(opt => opt.value);
          const errorLog = document.getElementById('errorLog').value || '';
          const summary = document.getElementById('summary').value || '';
          // Reset follow-up counter for a new diagnosis
          followUpCount = 0;
          vscode.postMessage({
            command: 'diagnose',
            files: selectedFiles,
            error_log: errorLog,
            summary: summary
          });
        });
        // Render a diff patch into a pre element with styled lines
        function renderDiff(patch) {
          const pre = document.createElement('pre');
          pre.className = 'diff-viewer';
          const lines = patch.split('\n');
          lines.forEach(line => {
            const div = document.createElement('div');
            if (line.startsWith('+')) {
              div.className = 'diff-line added';
            } else if (line.startsWith('-')) {
              div.className = 'diff-line removed';
            } else if (line.startsWith('@@')) {
              div.className = 'diff-line header';
            } else {
              div.className = 'diff-line';
            }
            div.textContent = line;
            pre.appendChild(div);
          });
          return pre;
        }
        // Receive messages from the extension
        window.addEventListener('message', event => {
          const message = event.data;
          if (message.command === 'diagnoseResult') {
            const data = message.data || {};
            // Update root cause banner
            if (data.root_cause) {
              rootBanner.style.display = 'block';
              rootBanner.textContent = data.root_cause;
            } else {
              rootBanner.style.display = 'none';
            }
            // Render patches
            patchesContainer.innerHTML = '';
            const patches = Array.isArray(data.patches) ? data.patches : [];
            patches.forEach((patch, idx) => {
              const title = document.createElement('div');
              title.textContent = 'Patch ' + (idx + 1);
              title.style.fontWeight = 'bold';
              patchesContainer.appendChild(title);
              patchesContainer.appendChild(renderDiff(patch));
            });
            // Handle follow-up
            if (data.follow_up) {
              followUpContainer.style.display = 'block';
              followUpQuestion.textContent = data.follow_up;
              if (followUpCount >= 3) {
                submitFollowUp.style.display = 'none';
                escalButton.style.display = 'inline-block';
              } else {
                submitFollowUp.style.display = 'inline-block';
                escalButton.style.display = 'none';
              }
            } else {
              followUpContainer.style.display = 'none';
            }
          }
        });
        // Submit follow-up answer
        submitFollowUp.addEventListener('click', () => {
          const answer = followUpAnswer.value || '';
          followUpAnswer.value = '';
          followUpCount++;
          vscode.postMessage({ command: 'followUp', answer });
        });
        // Escalate button
        escalButton.addEventListener('click', () => {
          vscode.postMessage({ command: 'escalate' });
        });
      }());
    </script>
  </body>
  </html>`;
}
function activate(context) {
    // Register the command that triggers the debug copilot
    const disposable = vscode.commands.registerCommand('extension.debugWithAICopilot', () => __awaiter(this, void 0, void 0, function* () {
        // Ensure a workspace is open
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('AI Debugging Copilot requires an open workspace.');
            return;
        }
        const workspaceRoot = workspaceFolders[0].uri.fsPath;
        // Determine default set of files (git diff)
        const changedFiles = getChangedFiles(workspaceRoot);
        // Create and show a new Webview panel
        const panel = vscode.window.createWebviewPanel('aiDebugCopilot', 'AI Debugging Copilot', vscode.ViewColumn.One, {
            enableScripts: true,
        });
        // Set the webview's HTML content
        panel.webview.html = getWebviewContent(panel.webview, context.extensionUri, changedFiles);
        // Listen for messages from the webview
        panel.webview.onDidReceiveMessage((message) => __awaiter(this, void 0, void 0, function* () {
            if (message.command === 'diagnose') {
                const selectedFiles = message.files;
                const errorLog = message.error_log || '';
                const summary = message.summary || '';
                // Prepare file payloads
                const filesPayload = [];
                for (const file of selectedFiles) {
                    const filePath = path.join(workspaceRoot, file);
                    try {
                        const data = yield fs.promises.readFile(filePath);
                        const compressed = gzipBase64(data);
                        filesPayload.push({ filename: file, content: compressed });
                    }
                    catch (err) {
                        vscode.window.showWarningMessage(`Could not read file ${file}: ${err}`);
                    }
                }
                // Build the payload object
                const payload = {
                    files: filesPayload,
                    error_log: errorLog,
                    summary: summary
                };
                // Save session in memory using timestamp as key
                const sessionId = Date.now().toString();
                sessions[sessionId] = payload;
                lastPayload = payload;
                followUpCount = 0;
                yield sendPayloadToBackend(payload);
            }
            else if (message.command === 'followUp') {
                // Append the follow‑up answer to the summary and resend
                const answer = message.answer || '';
                if (lastPayload) {
                    lastPayload = Object.assign(Object.assign({}, lastPayload), { summary: (lastPayload.summary || '') + '\n\n' + answer });
                    followUpCount += 1;
                    yield sendPayloadToBackend(lastPayload);
                }
            }
            else if (message.command === 'escalate') {
                vscode.window.showInformationMessage('Escalation requested. Please seek assistance from a human teammate.');
            }
        }));
        // Helper to post a payload to the backend and return result to webview
        function sendPayloadToBackend(payload) {
            return __awaiter(this, void 0, void 0, function* () {
                try {
                    const response = yield fetch('http://localhost:8000/diagnose', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const json = yield response.json();
                    panel.webview.postMessage({ command: 'diagnoseResult', data: json });
                }
                catch (err) {
                    panel.webview.postMessage({ command: 'diagnoseResult', data: { error: 'Failed to contact backend: ' + err } });
                }
            });
        }
    }));
    context.subscriptions.push(disposable);
}
function deactivate() { }
//# sourceMappingURL=extension.js.map