#!/usr/bin/env python3
"""Basic tests for mados-pdf-viewer - verify modules compile."""

import py_compile
import os

test_dir = os.path.dirname(os.path.abspath(__file__))
repo_dir = os.path.dirname(test_dir)

def test_translations_compile():
    """Test translations.py compiles without syntax errors."""
    py_compile.compile(f"{repo_dir}/translations.py", doraise=True)


def test_theme_compile():
    """Test theme.py compiles without syntax errors."""
    py_compile.compile(f"{repo_dir}/theme.py", doraise=True)


def test_annotations_compile():
    """Test annotations.py compiles without syntax errors."""
    py_compile.compile(f"{repo_dir}/annotations.py", doraise=True)


def test_app_compile():
    """Test app.py compiles without syntax errors."""
    py_compile.compile(f"{repo_dir}/app.py", doraise=True)


if __name__ == "__main__":
    test_translations_compile()
    test_theme_compile()
    test_annotations_compile()
    test_app_compile()
    print("All tests passed!")
