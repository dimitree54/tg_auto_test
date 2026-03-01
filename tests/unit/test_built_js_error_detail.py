"""Reproduce bug: built app.js does not extract error detail from JSON response body.

The Demo UI frontend shows raw HTTP status like
"[Upload error: POST /api/photo failed: 422 Unprocessable Entity]"
instead of the server's descriptive error message like
"Bot did not respond to the message. It may not have a handler for this message type."

Root cause: the TypeScript source (web/src/api/http.ts) was updated to read the
``detail`` field from JSON error responses, but the built JS artifact
(tg_auto_test/demo_ui/server/static/ui/app.js) was never rebuilt from the
updated source. The shipped app.js still contains the old synchronous
``httpError`` that ignores the response body entirely.

These tests verify the built JS contains the necessary error-detail extraction
logic. They FAIL against the current (stale) build and will PASS once app.js
is rebuilt from the fixed TypeScript source.
"""

from pathlib import Path
import re

_REPO_ROOT = Path(__file__).resolve().parents[2]
_APP_JS = _REPO_ROOT / "tg_auto_test" / "demo_ui" / "server" / "static" / "ui" / "app.js"


def _read_app_js() -> str:
    return _APP_JS.read_text(encoding="utf-8")


def _extract_fn_body(js: str, start: int) -> str:
    """Extract a function body from its declaration start to the matching }."""
    brace_pos = js.index("{", start)
    depth = 0
    for i in range(brace_pos, len(js)):
        if js[i] == "{":
            depth += 1
        elif js[i] == "}":
            depth -= 1
            if depth == 0:
                return js[start : i + 1]
    return js[start:]


def _find_http_error_fn(js: str) -> tuple[str, str]:
    """Return (minified_name, function_text) of the httpError function.

    httpError is identified by its fallback error template containing
    ``failed:`` combined with ``.status`` and ``.statusText``.
    """
    pattern = re.compile(r"(?:async\s+)?function\s+(\w+)\s*\(")
    for m in pattern.finditer(js):
        body = _extract_fn_body(js, m.start())
        if "failed:" in body and ".statusText" in body:
            return m.group(1), body
    msg = "Could not locate the httpError function in app.js"
    raise AssertionError(msg)


def test_http_error_function_is_async() -> None:
    """The httpError helper must be async so it can ``await res.json()``."""
    js = _read_app_js()
    fn_name, fn_text = _find_http_error_fn(js)

    assert fn_text.startswith("async"), (
        f"BUG: httpError (minified as '{fn_name}') is a synchronous "
        "function in the built app.js. It must be async to await "
        "res.json() and extract the error detail. Rebuild app.js from "
        "the updated TypeScript source."
    )


def test_http_error_reads_json_detail() -> None:
    """The httpError helper must read ``.detail`` from the JSON error body."""
    js = _read_app_js()
    fn_name, fn_text = _find_http_error_fn(js)

    assert ".json()" in fn_text, (
        f"BUG: httpError (minified as '{fn_name}') does not call .json() "
        "to parse the error response body. The built app.js ignores the "
        "server's JSON error detail. Rebuild from the updated "
        "TypeScript source."
    )

    assert ".detail" in fn_text, (
        f"BUG: httpError (minified as '{fn_name}') does not access "
        ".detail on the parsed JSON body. The built app.js cannot "
        "extract the server's descriptive error message. Rebuild from "
        "the updated TypeScript source."
    )


def test_http_error_callers_use_await() -> None:
    """All callers of httpError must ``await`` it since it is now async."""
    js = _read_app_js()
    fn_name, _ = _find_http_error_fn(js)

    throw_pattern = re.compile(rf"throw\s+(await\s+)?{re.escape(fn_name)}\s*\(")
    throw_matches = list(throw_pattern.finditer(js))
    assert len(throw_matches) > 0, f"No throw sites found for httpError function '{fn_name}'"

    for m in throw_matches:
        assert m.group(1) is not None, (
            f"BUG: Found 'throw {fn_name}(...)' without await. Since "
            "httpError is async (returns a Promise), callers must use "
            f"'throw await {fn_name}(...)'. Without await, a rejected "
            "Promise is thrown instead of the Error object, so "
            "error.message is never the server's detail text. Rebuild "
            "app.js from the updated TypeScript source."
        )
