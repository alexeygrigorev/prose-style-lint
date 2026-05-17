"""Tests for the stylint package import surface."""

from stylint import Finding, Tag, check_page, count_sentences, find_gerund_starts
from stylint.discovery import iter_markdown_pages


def test_package_exports_public_api():
    assert Tag.BOLD.value == "bold"
    assert Finding.__name__ == "Finding"
    assert check_page.__name__ == "check_page"
    assert count_sentences("One. Two.") == 2
    assert find_gerund_starts("Reading this, we see the point.") == ["Reading"]


def test_package_exposes_discovery_helpers():
    assert iter_markdown_pages([]) == []
