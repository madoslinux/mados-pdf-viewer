# madOS PDF Viewer

A professional PDF viewing application for madOS (Arch Linux) featuring PDF rendering via Poppler, text annotations, digital signatures, form filling, save/print functionality, and Nord theme styling.

## Features

- **PDF Rendering**: High-quality PDF display using Poppler/Cairo
- **Text Annotations**: Add, move, and clear text annotations on any page
- **Digital Signatures**: Draw signatures or place image signatures on documents
- **Form Fields**: Fill interactive PDF forms
- **Save & Print**: Save annotated PDFs and print documents
- **Navigation**: Page navigation, zoom controls, fit-to-width/page modes
- **Keyboard Shortcuts**: Arrow keys (navigate), +/- (zoom), Ctrl+O (open), Ctrl+S (save)
- **Nord Theme**: Beautiful dark theme following the Nord color palette

## Requirements

- Python 3
- GTK3 (gir1.2-gtk-3.0)
- Poppler (gir1.2-poppler-0.18)
- Cairo (python-cairo)

## Installation

```bash
# Run with Python module
python -m mados_pdf_viewer

# Or run directly
python __main__.py

# With a PDF file
python -m mados_pdf_viewer document.pdf
```

## Architecture

### Frontend (GTK3 UI)

```
+---------------------------------------------------------------+
|                      PDFViewerApp                             |
|  +-------------+  +-------------+  +--------------------+   |
|  |   Toolbar   |  |   Canvas    |  |    Statusbar       |   |
|  | (buttons,   |  | (PDF render |  | (page info, zoom)  |   |
|  |  controls)  |  |  + overlays)|  |                    |   |
|  +-------------+  +-------------+  +--------------------+   |
+---------------------------------------------------------------+
```

### Backend (Core Modules)

```
+---------------------------------------------------------------+
|  renderer.py - Poppler/Cairo Engine                          |
|  +---------------------------------------------------------+  |
|  | PDFDocument: load, get_page, metadata                  |  |
|  | PageRenderer: render page to cairo surface             |  |
|  +---------------------------------------------------------+  |
+----------------------------+----------------------------------+
                             |
                             v
+---------------------------------------------------------------+
|  annotations.py - Annotation Management                       |
|  +---------------------------------------------------------+  |
|  | TextAnnotation: position, text, color                   |  |
|  | SignaturePlacement: position, image surface             |  |
|  | SignaturePad/SignatureDialog: draw capture               |  |
|  | FormFieldManager: PDF form field handling              |  |
|  +---------------------------------------------------------+  |
+----------------------------+----------------------------------+
                             |
                             v
+---------------------------------------------------------------+
|  theme.py - Nord CSS Theme                                   |
|  +---------------------------------------------------------+  |
|  | apply_theme(): load Nord-themed CSS                     |  |
|  +---------------------------------------------------------+  |
+----------------------------+----------------------------------+
                             |
                             v
+---------------------------------------------------------------+
|  translations.py - i18n Support                              |
|  +---------------------------------------------------------+  |
|  | get_text(): retrieve translated strings                 |  |
|  | detect_system_language(): auto-detect locale            |  |
|  +---------------------------------------------------------+  |
+---------------------------------------------------------------+
```

## Sequence Diagrams

### Open PDF File

```mermaid
sequenceDiagram
    participant User
    participant UI as PDFViewerApp
    participant Doc as PDFDocument
    participant Renderer as PageRenderer
    participant Canvas as GTK Canvas

    User->>UI: File > Open (Ctrl+O)
    UI->>UI: _on_open()
    UI->>User: Show FileChooserDialog
    User->>UI: Select PDF file
    UI->>Doc: load(filepath)
    Doc->>Doc: Poppler.Document.new_from_file()
    Doc-->>UI: document loaded
    UI->>UI: Reset state (page, annotations, cache)
    UI->>Renderer: Update with new document
    UI->>Canvas: queue_draw()
    Canvas->>Renderer: Request page render
    Renderer-->>Canvas: Return cairo surface
    Canvas->>User: Display rendered PDF
```

### Render Page with Annotations

```mermaid
sequenceDiagram
    participant Canvas as GTK Canvas
    participant Renderer as PageRenderer
    participant Doc as PDFDocument
    participant Annot as Annotations

    Canvas->>Doc: get_page(page_index)
    Doc-->>Canvas: Poppler.Page
    Canvas->>Renderer: render(page, scale)
    Renderer->>Renderer: Create cairo surface
    Renderer->>Page: page.render(context)
    Renderer-->>Canvas: Rendered surface
    Canvas->>Canvas: Draw PDF background
    loop For each annotation on page
        Canvas->>Annot: get_annotation()
        Annot-->>Canvas: annotation data
        Canvas->>Canvas: Draw annotation overlay
    end
    loop For each signature on page
        Canvas->>Canvas: Draw signature image
    end
    Canvas->>Canvas: Complete page render
```

### Add Text Annotation

```mermaid
sequenceDiagram
    participant User
    participant Canvas as GTK Canvas
    participant UI as PDFViewerApp
    participant Annot as TextAnnotation

    User->>UI: Click "Add Text" button
    UI->>UI: Set mode = ADD_TEXT
    User->>Canvas: Click on page location
    Canvas->>UI: _on_canvas_button_press(event)
    UI->>UI: Check mode == ADD_TEXT
    UI->>UI: _place_text_annotation(page_idx, x, y)
    UI->>Annot: TextAnnotationDialog()
    User->>Annot: Enter annotation text
    Annot-->>UI: Return text
    UI->>UI: Store annotation in self.annotations
    UI->>Canvas: queue_draw()
    Canvas->>User: Display annotation on page
```

### Add Digital Signature

```mermaid
sequenceDiagram
    participant User
    participant UI as PDFViewerApp
    participant Dialog as SignatureDialog
    participant Pad as SignaturePad
    participant Canvas as GTK Canvas

    User->>UI: Click "Draw Signature"
    UI->>Dialog: SignatureDialog()
    Dialog->>Pad: SignaturePad() for drawing
    User->>Pad: Draw signature with mouse
    Pad->>User: Show drawing preview
    User->>Dialog: Confirm/Apply
    Dialog-->>UI: Return signature surface
    UI->>UI: Set mode = PLACE_SIGNATURE
    User->>Canvas: Click to place signature
    Canvas->>UI: _on_canvas_button_press(event)
    UI->>UI: _place_signature(page_idx, x, y)
    UI->>UI: Store in self.signatures
    UI->>Canvas: queue_draw()
    Canvas->>User: Display signature on page
```

### Fill PDF Form

```mermaid
sequenceDiagram
    participant User
    participant UI as PDFViewerApp
    participant FormMgr as FormFieldManager
    participant Canvas as GTK Canvas

    User->>UI: Toggle "Highlight Fields"
    UI->>FormMgr: highlight_fields = True
    UI->>Canvas: queue_draw()
    Canvas->>FormMgr: get_fields(page_idx)
    FormMgr-->>Canvas: Return form fields
    Canvas->>User: Highlight interactive fields
    
    User->>UI: Click "Fill Form" mode
    UI->>UI: Set mode = FILL_FORM
    User->>Canvas: Click on form field
    Canvas->>UI: _handle_form_click(page_idx, x, y)
    UI->>FormMgr: get_field_at(page_idx, x, y)
    FormMgr-->>UI: Return field
    UI->>UI: FormFieldDialog(field)
    User->>UI: Enter form data
    UI->>FormMgr: Update field value
    UI->>Canvas: queue_draw()
    User->>User: See filled form field
```

## File Structure

```
mados-pdf-viewer/
├── AGENTS.md           # Agent guidelines
├── .gitignore          # Git ignore rules
├── __init__.py         # Package metadata
├── __main__.py         # Entry point
├── app.py              # Main window (GTK), toolbar, canvas
├── renderer.py         # Poppler/Cairo PDF rendering
├── annotations.py     # Text annotations, signatures, form fields
├── theme.py            # Nord CSS theme
└── translations.py     # i18n strings
```

## Interaction Modes

The application uses an `InteractionMode` enum to manage different user interaction states:

```python
class InteractionMode:
    NORMAL = "normal"           # Default viewing mode
    ADD_TEXT = "add_text"      # Adding text annotations
    PLACE_SIGNATURE = "place_signature"  # Placing signatures
    FILL_FORM = "fill_form"    # Filling PDF forms
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Arrow Left/Right | Previous/Next page |
| Arrow Up/Down | Previous/Next page |
| + / - | Zoom In/Out |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save As |
| Ctrl+P | Print |
| Home | First page |
| End | Last page |

## License

MIT License