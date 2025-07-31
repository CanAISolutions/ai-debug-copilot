# AI Debugging Copilot - Complete Usage Guide

## 🎯 What is AI Debugging Copilot?

AI Debugging Copilot is a VS Code extension that automatically diagnoses test failures and suggests fixes. It combines:

- **Smart test detection** - Automatically runs your test suite and captures failures
- **AI-powered diagnosis** - Uses OpenAI to analyze code and error logs
- **Interactive fixes** - Shows patches with colored diffs and follow-up questions
- **Continuous learning** - Improves accuracy through synthetic test scenarios

## 🚀 Getting Started

### Prerequisites
- VS Code with the AI Debugging Copilot extension installed
- Python 3.8+ and Node.js 14+
- A project with tests (Vitest, Jest, or pytest)

### 1. Setup Your Environment

```bash
# Clone and setup
git clone <your-repo>
cd <your-repo>

# Install Python dependencies
python -m venv .venv
# Windows:
.venv\Scripts\Activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt

# Install Node dependencies
npm ci

# Start the backend (in a separate terminal)
cd app
uvicorn main:app --reload --port 8000
```

### 2. Configure OpenAI (Optional but Recommended)

For real AI diagnosis instead of simulation:

1. Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a `.env` file in your project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Restart the backend

## 🎮 How to Use

### Step 1: Trigger the Diagnosis

**Method A: Command Palette**
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "AI Debug Copilot: Diagnose"
3. Press Enter

**Method B: Extension Command**
1. Open the Extensions panel (`Ctrl+Shift+X`)
2. Find "AI Debugging Copilot"
3. Click "Diagnose" in the extension details

### Step 2: What Happens Automatically

The extension will:

1. **Detect your test framework** - Looks for `package.json` scripts (vitest, jest) or `pytest`
2. **Run failing tests** - Executes your test suite and captures failures
3. **Collect relevant files** - Gathers changed files from git and failing test files
4. **Build diagnostic payload** - Compresses and sends code + error logs to the AI backend

### Step 3: Review the Diagnosis

The WebView panel will show:

- **Root Cause Banner** - AI's analysis of what went wrong
- **Confidence Level** - How certain the AI is about the diagnosis
- **Colored Diff Patches** - Suggested fixes with green (added) and red (removed) lines
- **Follow-up Questions** - AI may ask for more context

### Step 4: Apply Fixes

1. **Review the patches** - Each patch shows exactly what to change
2. **Click "Apply Patch"** - The extension will modify your files
3. **Re-run tests** - Verify the fix worked
4. **Answer follow-ups** - If the AI asks questions, provide more context

## 📋 Detailed Workflow Examples

### Example 1: Fixing a Missing Import

**Scenario**: Your test fails with `ModuleNotFoundError: No module named 'utils'`

1. **Trigger diagnosis** - The extension runs tests and captures the error
2. **AI analyzes** - Identifies missing import in the test file
3. **Shows patch**:
   ```diff
   + from utils import helper_function
   ```
4. **Apply and verify** - Test passes after applying the patch

### Example 2: Circular Import Issue

**Scenario**: Tests fail with circular import errors

1. **Extension collects** - All related files and the import chain
2. **AI diagnoses** - Identifies the circular dependency
3. **Suggests refactor** - Moves shared code to a separate module
4. **Follow-up questions** - AI asks about the intended architecture

### Example 3: Assertion Failures

**Scenario**: Test assertions are failing

1. **Extension captures** - The actual vs expected values
2. **AI analyzes** - Compares the logic with the test expectations
3. **Suggests fixes** - Either updates the test or fixes the implementation
4. **Shows confidence** - Indicates whether it's a test bug or code bug

## 🛠 Advanced Features

### Custom Test Commands

If your project uses custom test commands, the extension will detect them from `package.json`:

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest --coverage"
  }
}
```

### File Selection

The WebView shows a list of relevant files:
- **Changed files** - From git diff
- **Failing test files** - Automatically detected
- **Related files** - Based on import/export relationships

You can:
- Select/deselect files to include in diagnosis
- Add custom error logs
- Provide context about recent changes

### Follow-up Conversations

The AI can ask follow-up questions to get more context:

1. **"What were you trying to achieve?"** - Helps understand intent
2. **"Are there any specific requirements?"** - Clarifies constraints
3. **"Can you show me the expected output?"** - Validates expectations

### Escalation

After 3 follow-up exchanges, an "Escalate" button appears:
- Use this when the AI needs human intervention
- Suggests seeking help from teammates
- Logs the conversation for future improvement

## 🔧 Troubleshooting

### Backend Connection Issues

**Error**: "Failed to contact backend"

**Solutions**:
1. Ensure the backend is running: `uvicorn main:app --reload --port 8000`
2. Check if port 8000 is available
3. Verify firewall settings

### Test Detection Problems

**Issue**: Extension doesn't find your tests

**Solutions**:
1. Ensure tests are in standard locations (`__tests__/`, `tests/`, `*.test.js`, `*.spec.js`)
2. Check `package.json` has test scripts
3. Verify test framework is properly configured

### OpenAI API Issues

**Issue**: Getting simulation responses instead of real AI

**Solutions**:
1. Verify `.env` file has `OPENAI_API_KEY=your_key`
2. Check API key is valid and has credits
3. Restart the backend after adding the key

### Performance Tips

1. **Selective file inclusion** - Only include relevant files for faster diagnosis
2. **Clear error logs** - Provide specific error messages for better accuracy
3. **Recent changes context** - Describe what you changed recently

## 🧪 Testing the System

### Demo with Intentional Failures

The project includes demo files with intentional failures:

```bash
# Run the demo script
# Windows:
.\run_demo.ps1

# Mac/Linux:
./run_demo.sh
```

This will:
1. Start the backend
2. Run failing tests
3. Send diagnostic request
4. Apply suggested fixes
5. Re-run tests to verify

### Manual Testing

1. **Create a failing test**:
   ```javascript
   test('intentional failure', () => {
     expect(1 + 1).toBe(3); // This will fail
   });
   ```

2. **Trigger diagnosis** - Use the extension command

3. **Review the fix** - AI should suggest changing `3` to `2`

4. **Apply and verify** - Test should pass

## 📊 Understanding the Output

### Confidence Levels

- **0.9+ (High)** - AI is very confident about the diagnosis
- **0.7-0.9 (Medium)** - AI has good confidence but may need follow-up
- **<0.7 (Low)** - AI is uncertain, consider providing more context

### Patch Format

Patches use standard git diff format:
- `+` lines (green) = additions
- `-` lines (red) = deletions
- `@@` lines (purple) = file locations

### Error Messages

- **"Simulation mode"** - No OpenAI API key configured
- **"Failed to contact backend"** - Backend not running
- **"No tests found"** - Test framework not detected

## 🔄 Continuous Improvement

### Feedback Loop

The system learns from each interaction:
1. **Metrics logging** - Response times and confidence levels
2. **Prompt evaluation** - Synthetic tests validate accuracy
3. **User feedback** - Follow-up questions improve future diagnoses

### Contributing Improvements

1. **Add test fixtures** - Create new scenarios in `tests/prompt_fixtures/`
2. **Improve prompts** - Modify `app/prompt_builder.py`
3. **Report issues** - Use GitHub issues for bugs or feature requests

## 🎯 Best Practices

### For Optimal Results

1. **Keep tests focused** - One assertion per test when possible
2. **Provide context** - Describe recent changes in the summary
3. **Include error logs** - Copy-paste the full error message
4. **Select relevant files** - Don't include unrelated code

### When to Use

- **Test failures** - Primary use case
- **Build errors** - Compilation or bundling issues
- **Runtime errors** - Application crashes or exceptions
- **Performance issues** - Slow tests or timeouts

### When to Escalate

- **Complex architectural issues** - May need human design decisions
- **External dependencies** - Third-party library problems
- **Environment-specific issues** - OS, version, or configuration problems
- **Security concerns** - Sensitive code or authentication issues

---

## 🆘 Getting Help

- **Documentation**: Check this guide and the main README
- **Issues**: Use GitHub issues for bugs or feature requests
- **Community**: Join discussions in the project repository
- **Development**: Check `ROADMAP.md` for upcoming features

---

*This guide covers the complete usage of AI Debugging Copilot. For technical details, see the main README.md and code documentation.* 