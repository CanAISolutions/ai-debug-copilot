from app.main import choose_model, decode_files, FilePayload
import base64, gzip


def test_choose_model_trivial():
    files = [FilePayload(filename="a.py", content="")] * 1
    assert choose_model("short log", files) == "gpt-4o-mini"


def test_choose_model_large():
    long_log = "x" * 600
    files = [FilePayload(filename=f"file{i}.py", content="") for i in range(5)]
    assert choose_model(long_log, files) == "gpt-4o"


def test_decode_files_valid():
    raw = b"print('hi')\n"
    encoded = base64.b64encode(gzip.compress(raw)).decode()
    payload = [FilePayload(filename="foo.py", content=encoded)]
    decoded = decode_files(payload)
    assert decoded[0]['content'].startswith("print('hi')")


def test_decode_files_invalid():
    payload = [FilePayload(filename="bad.py", content="not-base64!")]
    decoded = decode_files(payload)
    assert decoded[0]['content'] == ""
