"""Tests that verify all NotImplementedError stubs are classified and tracked."""

import ast
from pathlib import Path

from tests.unit.stub_classification_registry import IMPLEMENTABLE_COUNT, STUB_REGISTRY, StubCategory

_TEST_UTILS_DIR = Path("tg_auto_test/test_utils")


def _is_del_stmt(node: ast.stmt) -> bool:
    return isinstance(node, ast.Delete)


def _is_raise_not_implemented(node: ast.stmt) -> bool:
    if not isinstance(node, ast.Raise):
        return False
    exc = node.exc
    if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
        return exc.func.id == "NotImplementedError"
    return isinstance(exc, ast.Name) and exc.id == "NotImplementedError"


def _is_pure_stub(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """A pure stub has only `del` statements followed by exactly one `raise NotImplementedError`."""
    body = func_node.body
    # Skip docstrings
    stmts = body[1:] if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) else body
    if not stmts:
        return False
    # All but last must be del, last must be raise NotImplementedError
    for stmt in stmts[:-1]:
        if not _is_del_stmt(stmt):
            return False
    return _is_raise_not_implemented(stmts[-1])


def _scan_stubs() -> set[tuple[str, str]]:
    """Scan all .py files under test_utils and return (module, method) tuples for pure stubs."""
    found: set[tuple[str, str]] = set()
    for py_file in sorted(_TEST_UTILS_DIR.glob("*.py")):
        module_name = py_file.stem
        tree = ast.parse(py_file.read_text())
        for class_node in ast.walk(tree):
            if not isinstance(class_node, ast.ClassDef):
                continue
            for node in class_node.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_pure_stub(node):
                    found.add((module_name, node.name))
    return found


def test_all_stubs_are_classified() -> None:
    """Every pure stub found by AST scanning must have a registry entry."""
    found_stubs = _scan_stubs()
    registry_keys = set(STUB_REGISTRY.keys())
    unclassified = found_stubs - registry_keys
    assert not unclassified, f"Unclassified stubs found: {sorted(unclassified)}"


def test_no_stale_classifications() -> None:
    """Every registry entry must still correspond to an actual pure stub in the source."""
    found_stubs = _scan_stubs()
    registry_keys = set(STUB_REGISTRY.keys())
    stale = registry_keys - found_stubs
    assert not stale, f"Stale registry entries (stub was implemented or removed): {sorted(stale)}"


def test_implementable_count_is_tracked() -> None:
    """Assert the exact count of IMPLEMENTABLE stubs to track debt."""
    actual = sum(1 for v in STUB_REGISTRY.values() if v == StubCategory.IMPLEMENTABLE)
    assert actual == IMPLEMENTABLE_COUNT, (
        f"IMPLEMENTABLE_COUNT constant ({IMPLEMENTABLE_COUNT}) does not match "
        f"actual count ({actual}). Update the registry."
    )
