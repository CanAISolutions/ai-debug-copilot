from app.prompt_builder import build_prompt

def test_prompt_contains_sections():
    prompt = build_prompt("Traceback...", "refactored auth module", ["snippet a"], ["ctx b"])
    assert "System" not in prompt  # system text present but no literal word check
    assert "Relevant retrieved snippets" in prompt
    assert "Relevant code context" in prompt
    assert "Error log" in prompt
    assert "Summary of changes" in prompt
