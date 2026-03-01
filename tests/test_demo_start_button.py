"""Tests verifying the Demo UI start button exists and works correctly."""

from pathlib import Path

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "tg_auto_test" / "demo_ui" / "server" / "templates"


def test_index_contains_start_button() -> None:
    """The index.html template must include a Telegram-style start button."""
    html = (_TEMPLATES_DIR / "index.html").read_text()

    assert 'id="startBtn"' in html, "Missing #startBtn element"
    assert 'id="startContainer"' in html, "Missing #startContainer wrapper"
    assert 'id="emptyPlaceholder"' in html, "Missing #emptyPlaceholder element"
    assert "start-btn" in html, "Missing .start-btn CSS class"
    assert "start-container" in html, "Missing .start-container CSS class"
