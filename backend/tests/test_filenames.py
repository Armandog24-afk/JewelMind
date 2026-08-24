"""Dedicated filename-safety tests. Previously sanitize_filename() was
only exercised indirectly through API tests using simple project names
that never hit its edge cases — a real, previously-undocumented test gap
found during Sprint 7 (Foundry)."""

from __future__ import annotations

from jewelmind.exporters.filenames import sanitize_filename


def test_allows_safe_characters_unchanged():
    assert sanitize_filename("My Ring-01.v2") == "My_Ring-01.v2"


def test_replaces_path_traversal_characters():
    result = sanitize_filename("../../etc/passwd")
    assert "/" not in result
    assert ".." not in result or result.count(".") <= 2  # collapsed, not a literal traversal token


def test_replaces_windows_reserved_path_characters():
    result = sanitize_filename('a:b*c?d"e<f>g|h')
    for ch in ':*?"<>|':
        assert ch not in result


def test_blank_name_falls_back_to_default():
    assert sanitize_filename("", default="jewelmind-export") == "jewelmind-export"
    assert sanitize_filename("   ", default="jewelmind-export") == "jewelmind-export"
    assert sanitize_filename("...", default="jewelmind-export") == "jewelmind-export"


def test_leading_dots_and_dashes_stripped():
    assert not sanitize_filename("-rm -rf").startswith("-")
    assert not sanitize_filename(".hidden").startswith(".")


def test_unicode_is_collapsed_not_passed_through():
    result = sanitize_filename("指輪リング")
    assert result.isascii()


def test_max_length_enforced():
    result = sanitize_filename("a" * 500)
    assert len(result) == 120


def test_windows_reserved_device_names_pass_through_unmodified():
    """Known, documented gap (Sprint 7): CON/PRN/AUX/NUL/COM1/LPT1 are not
    specially handled. This only affects the *client's* suggested
    save-as filename (Content-Disposition), never a server-side path —
    every server-side export file uses a random tempfile.mkstemp() name,
    never the sanitized project name directly. See
    docs/bible/09-foundry/206-filename-and-path-safety.md."""

    assert sanitize_filename("CON") == "CON"
    assert sanitize_filename("con") == "con"
