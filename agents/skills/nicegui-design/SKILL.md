---
name: nicegui-design
description: Create beautiful, modern web-based GUIs using NiceGUI framework. Use this skill whenever the user wants to build a user interface, create a web app, design a frontend, build a dashboard, or mentions anything related to Python UI development, web interfaces, or NiceGUI specifically. Apply this skill even if the user doesn't explicitly say "NiceGUI" but wants to create buttons, forms, dialogs, charts, tables, or any interactive web elements with Python.
metadata:
  author: wyzvrd
  version: 1.1.0
  framework: NiceGUI
  language: Python
  category: frontend-development
  tags: [ui, gui, web, python, nicegui, frontend, dashboard]
---

# NiceGUI Designer Skill

Build professional, modern web-based UIs using NiceGUI - a Python framework that creates browser-based interfaces.

## Core Philosophy

- **Backend-first**: Write Python, NiceGUI handles HTML/CSS/JS
- **Async-first**: UI updates on main thread only - never block with `time.sleep()` or heavy computations
- **Declarative UI**: Use `with` statements for nesting elements

## Architecture

```text
Your Python Code (NiceGUI) -> FastAPI + Socket.IO (WebSocket) -> Vue.js 3 + Quasar + Tailwind CSS
```

## Quick Start

```python
from nicegui import ui

with ui.card().classes('w-full max-w-md'):
    ui.label('Hello NiceGUI!').classes('text-h4')
    name = ui.input('Your name')
    ui.button('Greet', on_click=lambda: ui.notify(f'Hello {name.value}!'))

ui.run()
```

## Essential Elements by Category

### Layout & Structure

- **Containers**: `ui.card`, `ui.column`, `ui.row`, `ui.expansion`, `ui.tabs`
- **Page**: `ui.header`, `ui.footer`, `ui.left_drawer`, `ui.right_drawer`, `ui.page_sticky`

### User Input

- **Text**: `ui.input`, `ui.number`, `ui.textarea`
- **Selection**: `ui.select`, `ui.slider`, `ui.range`, `ui.checkbox`, `ui.switch`, `ui.radio`
- **Files**: `ui.upload`, `ui.download`

### Display & Data

- **Content**: `ui.label`, `ui.html`, `ui.markdown`, `ui.image`
- **Tables**: `ui.table`, `ui.aggrid`
- **Charts**: `ui.plotly`, `ui.echart`, `ui.highchart`, `ui.pyplot`

### Interaction & Feedback

- **Actions**: `ui.button`, `ui.icon_button`, `ui.fab`
- **Dialogs**: `ui.dialog`, `ui.notify`, `ui.notification`, `ui.tooltip`
- **Navigation**: `ui.link`, `ui.menu`, `ui.breadcrumbs`

**For complete element catalog with examples, see** [references/elements.md](references/elements.md)

## Critical Patterns

### 1. Declarative UI (The `with` Pattern)

```python
with ui.card().classes('w-full'):
    ui.label('Title').classes('text-h6')
    with ui.row():
        ui.input('Name')
        ui.button('Submit')
```

### 2. Async Event Handling (NEVER Block Main Thread)

```python
# CORRECT
async def handle_click():
    await asyncio.sleep(1)  # Non-blocking
    ui.notify('Done!')

# CPU-intensive work
from nicegui import run
async def process():
    result = await run.cpu_bound(heavy_function, data)
    ui.label(f'Result: {result}')

# WRONG - freezes UI
def bad_handler():
    time.sleep(5)  # NEVER do this
```

### 3. Styling (5 Layers)

```python
# 1. Element kwargs
ui.button('OK', color='primary', flat=True)

# 2. Tailwind CSS (RECOMMENDED)
ui.button('OK').classes('bg-blue-500 hover:bg-blue-600 shadow-lg')

# 3. Quasar props
ui.button('OK').props('outline rounded dense')

# 4. Inline styles
ui.button('OK').style('font-size: 20px')

# 5. Global CSS
ui.add_css('.custom { font-size: 20px }')
```

**For complete styling reference, see** [references/styling.md](references/styling.md)

### 4. State Management

```python
# Binding (auto-sync)
slider = ui.slider(0, 100)
label = ui.label()
slider.bind_value(label, 'text')

# Storage (persistent)
from nicegui import app
app.storage.user['theme'] = 'dark'  # Persists across sessions

# Reactive refreshable
@ui.refreshable
def user_list():
    for user in users:
        ui.label(user.name)

user_list.refresh()  # Re-render when data changes
```

**For more patterns (forms, tables, dashboards, etc.), see** [references/common-patterns.md](references/common-patterns.md)

## Page Structure

```python
from nicegui import ui

@ui.page('/')
def index():
    with ui.header().classes('bg-primary text-white'):
        ui.label('My App').classes('text-h6')

    with ui.left_drawer():
        ui.link('Home', '/')
        ui.link('Settings', '/settings')

    with ui.column().classes('p-4'):
        ui.label('Content here')

ui.run()
```

## Deployment

```python
# Development (localhost)
ui.run()

# Desktop app
ui.run(native=True, window_size=(800, 600))

# Production server
ui.run(host='0.0.0.0', port=8080, reload=False)
```

## Helper Scripts

This skill includes utility scripts in `scripts/`:

```bash
# Analyze requirements and suggest components
python scripts/component_helper.py --analyze "I need a dashboard with charts"

# Generate starter templates
python scripts/generate_template.py --type dashboard --output app.py

# Show styling patterns
python scripts/styling_guide.py --layout form
```

## When to Use What

| Task             | Recommended Elements                              |
| ---------------- | ------------------------------------------------- |
| Simple form      | `ui.card` + `ui.input` + `ui.button`              |
| Data table       | `ui.table` (simple) or `ui.aggrid` (complex)      |
| Dashboard        | `ui.row`/`ui.column` + cards + `ui.plotly`        |
| Settings page    | `ui.expansion` sections + `ui.switch`/`ui.select` |
| Wizard flow      | `ui.stepper`                                      |
| Image gallery    | `ui.carousel` or `ui.grid` with `ui.image`        |
| Chat interface   | `ui.chat_message` + `ui.scroll_area`              |
| 3D visualization | `ui.scene` (Three.js-based)                       |

## What To Do If You Don't Understand Something

### Escalation Protocol

1. **Check Skill References** (this skill has detailed refs in `references/`)

   - [references/elements.md](references/elements.md) - Full element catalog
   - [references/styling.md](references/styling.md) - Styling guide
   - [references/common-patterns.md](references/common-patterns.md) - Code patterns

1. **Official Documentation**

   - `nicegui.io/documentation` - API reference
   - `nicegui.io/examples` - 60+ working examples

1. **Debug with Browser Tools**

   ```python
   # Mark element for inspection
   my_element.mark('my-marker')

   # Run JavaScript in browser
   ui.run_javascript('console.log(getElement("my-marker"))')

   # Get computed properties
   value = await my_element.get_computed_prop('scrollHeight')
   ```

1. **Search GitHub Issues**

   - `github.com/zauberzeug/nicegui/issues`

1. **Fallback to Base Technologies**

   - Quasar Framework docs: `quasar.dev`
   - Vue 3 docs for reactivity patterns
   - Tailwind CSS docs for styling

1. **Community**

   - NiceGUI Discord
   - Reddit r/nicegui
   - Stack Overflow (tag: `nicegui`)

## Best Practices

- Use `with` for nesting elements
- Keep UI updates on main thread
- Offload heavy work with `run.cpu_bound()`/`run.io_bound()`
- Use Tailwind classes (`.classes()`) for styling
- Use binding for automatic value sync
- Use `ui.refreshable` for dynamic content
- Use `ui.notify()` for user feedback
- Never use `time.sleep()` in event handlers
- Never block the main thread

## Quick Reference: Most-Used

```python
# Basics
ui.label('Text')
ui.button('Click', on_click=callback)
ui.input('Label')
ui.select(['A', 'B', 'C'])

# Layout
with ui.card(): ...
with ui.row(): ...
with ui.column(): ...

# Actions
ui.notify('Message', type='positive')
with ui.dialog(): ...

# Data
ui.table(columns=columns, rows=rows)
ui.plotly(figure)

# Async helpers
await run.cpu_bound(func, args)
await run.io_bound(func, args)
ui.timer(interval, callback)
```

## Gotchas

- **Async Only**: Never use `time.sleep()` or blocking calls in event handlers. Use `await asyncio.sleep()` or `run.cpu_bound()`.
- **Thread Safety**: UI updates must happen on the main thread. Offload heavy work with `run.cpu_bound()` / `run.io_bound()`.
- **Binding Gotcha**: `bind_value()` creates a reference, not a copy. Modifying the bound object updates the UI automatically.
- **Storage Scope**: `app.storage.user` persists across sessions. `app.storage.general` is shared across all users.
- **Page Decorator**: `@ui.page('/')` routes must be defined before `ui.run()`. Each page function gets its own isolated context.
- **Native Mode**: `ui.run(native=True)` creates a desktop window. Requires `pywebview` package.
- **File vs UI**: "nicegui.py" is a file, not a UI request. Use filesystem skill for file operations.

______________________________________________________________________

**For detailed element documentation, styling guide, and code patterns, see the `references/` directory.**
