# AGENTS.md - madOS PDF Viewer

This file provides guidelines for agentic coding agents operating in this repository.

## Project Overview

madOS PDF Viewer is a professional PDF viewing application for madOS (Arch Linux). It features PDF rendering via Poppler, text annotations, digital signatures, form filling, save/print functionality, and Nord theme styling.

## Technology Stack

- **Language**: Python 3
- **UI Framework**: GTK3 (PyGObject)
- **PDF Engine**: Poppler (via GObject introspection)
- **Graphics**: Cairo
- **No external test framework** - the project has no tests

## Build/Lint/Test Commands

### Running the Application

```bash
# Run with Python module
python -m mados_pdf_viewer

# Or run directly
python __main__.py

# Or use the launcher
python -m mados_pdf_viewer <file.pdf>
```

### Testing

**No test framework is configured.** There are no test files in this repository. Do not attempt to run tests.

### Linting/Type Checking

**No linting or type checking tools are configured.** The project does not have:
- pyproject.toml
- setup.py
- pytest
- ruff
- mypy
- black
- isort

If adding linting is needed, recommend using `ruff` for linting and `mypy` for type checking.

## Code Style Guidelines

### Imports

```python
# Standard library first
import os
import math
import cairo

# Third-party (GTK/Poppler)
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Poppler", "0.18")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Poppler

# Local imports (relative)
from .renderer import PDFDocument, PageRenderer
from .annotations import (
    TextAnnotation,
    SignaturePlacement,
    SignaturePad,
    SignatureDialog,
)
from .translations import get_text, detect_system_language, DEFAULT_LANGUAGE
from .theme import apply_theme, hex_to_rgb_float
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `PDFViewerApp`, `PDFDocument`, `PageRenderer`)
- **Functions/Variables**: `snake_case` (e.g., `get_text`, `apply_theme`, `is_valid_page`)
- **Private attributes**: `self._private_name` (prefix with underscore)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MIN_ZOOM`, `MAX_ZOOM`, `PAGE_GAP`)
- **Modules**: `snake_case.py` (e.g., `renderer.py`, `annotations.py`, `theme.py`)
- **Enumerations**: `PascalCase` with uppercase constants (e.g., `InteractionMode.NORMAL`)

### Type Hints

Use type hints for properties and function signatures where helpful:

```python
@property
def zoom(self) -> float:
    return self._zoom

def load(self, filepath: str) -> None:
    ...
```

### Docstrings

Use Google-style docstrings with `Args:` and `Returns:` sections:

```python
def load(self, filepath: str) -> None:
    """Load a PDF file from disk.

    Args:
        filepath: Absolute or relative path to a PDF file.

    Raises:
        FileNotFoundError: If the file does not exist.
        RuntimeError: If Poppler cannot parse the file.
    """
```

### Error Handling

- Use try/except with specific exception types when possible
- For file operations: catch `FileNotFoundError`, `RuntimeError`, `GLib.Error`
- Silent failures with `pass` are acceptable for non-critical operations
- Use `_show_error()` method to display GTK error dialogs

### Code Patterns

**Private attributes with underscore prefix:**
```python
self._page_cache = {}
self._pending_signature_surface = None
self._dragging_annotation = None
```

**Section comments for code organization:**
```python
# ── Constants ─────────────────────────────────────────────────────────────────

MIN_ZOOM = 0.1
MAX_ZOOM = 5.0

# ══════════════════════════════════════════════════════════════════════════
#  UI Construction
# ══════════════════════════════════════════════════════════════════════════
```

**GTK signal connections:**
```python
self.window.connect("delete-event", self._on_delete_event)
self.window.connect("key-press-event", self._on_key_press)
button.connect("clicked", self._on_play_clicked)
```

**Property decorators for read-only access:**
```python
@property
def current_page(self) -> int:
    """Return the current page index (0-based)."""
    return self._current_page
```

### Formatting

- 4-space indentation (no tabs)
- Maximum line length: 100 characters (soft limit)
- Use f-strings for string formatting
- No trailing whitespace
- Blank lines between class methods and sections

### GTK-Specific Patterns

**Window initialization:**
```python
def _build_window(self):
    """Create the main application window."""
    self.window = Gtk.Window(title=get_text("title", self.lang))
    self.window.set_default_size(900, 700)
    self.window.set_position(Gtk.WindowPosition.CENTER)
    self.window.set_wmclass("mados-pdf-viewer", "mados-pdf-viewer")
    self.window.set_role("mados-pdf-viewer")
    self.window.connect("delete-event", self._on_delete_event)
```

**Toolbar construction:**
```python
def _build_toolbar(self):
    """Create the toolbar with all buttons and controls."""
    toolbar = Gtk.Toolbar()
    toolbar.set_style(Gtk.ToolbarStyle.ICONS)
    toolbar.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)
    self.main_box.pack_start(toolbar, False, False, 0)

    self._add_tool_button(toolbar, "document-open", "open", self._on_open)
```

**Drawing area with event handling:**
```python
self.canvas = Gtk.DrawingArea()
self.canvas.add_events(
    Gdk.EventMask.BUTTON_PRESS_MASK
    | Gdk.EventMask.BUTTON_RELEASE_MASK
    | Gdk.EventMask.POINTER_MOTION_MASK
    | Gdk.EventMask.SCROLL_MASK
)
self.canvas.connect("draw", self._on_canvas_draw)
self.canvas.connect("button-press-event", self._on_canvas_button_press)
```

### Poppler/Cairo Patterns

**PDF document loading:**
```python
def load(self, filepath: str) -> None:
    filepath = os.path.abspath(filepath)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"PDF file not found: {filepath}")

    uri = GLib.filename_to_uri(filepath, None)
    try:
        doc = Poppler.Document.new_from_file(uri, None)
    except GLib.Error as exc:
        raise RuntimeError(f"Failed to open PDF: {exc.message}") from exc

    self.document = doc
    self.n_pages = doc.get_n_pages()
```

**Page rendering to cairo surface:**
```python
def render(self, page: Poppler.Page, scale: float) -> cairo.ImageSurface:
    width = int(page.get_width() * scale)
    height = int(page.get_height() * scale)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)
    context.scale(scale, scale)
    page.render(context)
    return surface
```

## Common Tasks

### Adding a New Toolbar Button

In `app.py`, add to `_build_toolbar`:
```python
self._add_tool_button(toolbar, "icon-name", "tooltip_key", self._on_handler)
```

### Adding a New Keyboard Shortcut

In `app.py`, add to `_on_key_press`:
```python
def _on_key_press(self, widget, event):
    key = event.keyval
    if key == Gdk.KEY_KeyName:
        self._some_action()
        return True
    return False
```

### Adding a New Interaction Mode

In `app.py`, extend `InteractionMode` class and handle in event handlers:
```python
class InteractionMode:
    NORMAL = "normal"
    ADD_TEXT = "add_text"
    # Add new mode here
    
    # Handle in _on_canvas_button_press, _on_canvas_motion, etc.
```

### Adding New Translations

Edit `translations.py` - add the key to each language dictionary and update `DEFAULT_LANGUAGE`.

## File Structure

```
mados-pdf-viewer/
├── AGENTS.md           # This file
├── __init__.py         # Package metadata
├── __main__.py         # Entry point
├── app.py              # Main window (GTK), toolbar, canvas
├── renderer.py         # Poppler/Cairo PDF rendering
├── annotations.py     # Text annotations, signatures, form fields
├── theme.py            # Nord CSS theme
├── translations.py     # i18n strings
└── mados-pdf-viewer   # (if executable launcher exists)
```

## Important Notes

1. **No tests exist** - Do not attempt to run or add tests
2. **No CI/CD** - There are no GitHub Actions or similar
3. **Poppler required** - The app will not function without the poppler-glib library
4. **GTK3 only** - Uses GTK3 (not GTK4)
5. **Nord theme** - The app uses the Nord color palette for styling