# NiceGUI Common Patterns Reference

Quick reference for frequently-used NiceGUI patterns and solutions.

## Table of Contents

- [Form Handling](#form-handling)
- [Data Display](#data-display)
- [Navigation](#navigation)
- [State Management](#state-management)
- [Async Operations](#async-operations)
- [Styling Patterns](#styling-patterns)
- [Error Handling](#error-handling)

---

## Form Handling

### Input Validation

```python
from nicegui import ui

# Simple validation
name = ui.input('Name',
    validation={'Name is required': lambda v: v and len(v) > 0}
)

# Email validation
import re
email = ui.input('Email',
    validation={'Invalid email': lambda v: re.match(r'[^@]+@[^@]+\.[^@]+', v) is not None if v else True}
)

# Multiple validations
password = ui.input('Password', password=True,
    validation={
        'Min 8 characters': lambda v: len(v or '') >= 8,
        'Needs uppercase': lambda v: any(c.isupper() for c in v or ''),
        'Needs number': lambda v: any(c.isdigit() for c in v or ''),
    }
)
```

### Form with Dynamic Fields

```python
from nicegui import ui

form_data = {}

with ui.card():
    # Type selector
    form_type = ui.select(['Personal', 'Business'], label='Form Type')

    # Dynamic container
    dynamic_fields = ui.element('div')

    def update_fields():
        dynamic_fields.clear()
        with dynamic_fields:
            if form_type.value == 'Personal':
                ui.input('Full Name', on_change=lambda e: form_data.update(name=e.value))
                ui.input('Date of Birth', on_change=lambda e: form_data.update(dob=e.value))
            elif form_type.value == 'Business':
                ui.input('Company Name', on_change=lambda e: form_data.update(company=e.value))
                ui.input('Tax ID', on_change=lambda e: form_data.update(tax_id=e.value))

    form_type.on_change(update_fields)
    update_fields()  # Initial render
```

---

## Data Display

### Paginated Table

```python
from nicegui import ui

all_rows = [{'id': i, 'name': f'Item {i}'} for i in range(100)]
page_size = 10
current_page = ui.state(1)

table = ui.table(
    columns=[{'name': 'id', 'label': 'ID'}, {'name': 'name', 'label': 'Name'}],
    rows=all_rows[:page_size]
).classes('w-full')

with ui.row():
    def prev_page():
        if current_page.value > 1:
            current_page.value -= 1
            update_table()

    def next_page():
        max_page = (len(all_rows) + page_size - 1) // page_size
        if current_page.value < max_page:
            current_page.value += 1
            update_table()

    ui.button('Previous', on_click=prev_page)
    page_label = ui.label(f'Page {current_page.value}')
    ui.button('Next', on_click=next_page)

def update_table():
    start = (current_page.value - 1) * page_size
    end = start + page_size
    table.rows = all_rows[start:end]
    page_label.set_text(f'Page {current_page.value} of {(len(all_rows) + page_size - 1) // page_size}')
```

### Searchable List

```python
from nicegui import ui

items = ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry', 'Fig', 'Grape']

search = ui.input('Search', placeholder='Type to filter...')
list_container = ui.element('div')

def update_list():
    list_container.clear()
    filtered = [i for i in items if search.value.lower() in i.lower()] if search.value else items
    with list_container:
        for item in filtered:
            ui.label(item)

search.on_change(update_list)
update_list()
```

---

## Navigation

### SPA Router

```python
from nicegui import ui, app

# Simple SPA with view switching
current_view = ui.state('home')
content = ui.element('div')

def show_view(view_name):
    current_view.value = view_name
    content.clear()
    with content:
        if view_name == 'home':
            show_home()
        elif view_name == 'about':
            show_about()
        elif view_name == 'contact':
            show_contact()

def show_home():
    ui.label('Home Page').classes('text-h3')
    ui.label('Welcome to the home page')

def show_about():
    ui.label('About Page').classes('text-h3')
    ui.label('About us content here')

def show_contact():
    ui.label('Contact Page').classes('text-h3')
    ui.input('Name')
    ui.input('Email')
    ui.textarea('Message')
    ui.button('Send')

# Navigation
with ui.row():
    ui.button('Home', on_click=lambda: show_view('home'))
    ui.button('About', on_click=lambda: show_view('about'))
    ui.button('Contact', on_click=lambda: show_view('contact'))

show_view('home')
```

### Nested Layout

```python
from nicegui import ui

with ui.row().classes('h-screen'):
    # Sidebar
    with ui.column().classes('w-64 bg-gray-100 p-4'):
        ui.label('Menu').classes('text-h6 mb-4')
        ui.link('Dashboard', '/dashboard')
        ui.link('Analytics', '/analytics')
        ui.link('Settings', '/settings')

    # Main content
    with ui.column().classes('flex-1 p-6'):
        ui.label('Page Title').classes('text-h4')
        # Page content
```

---

## State Management

### Global State

```python
from nicegui import ui, app

# App-level state (shared across all clients)
app.storage.general['counter'] = app.storage.general.get('counter', 0)

def increment():
    app.storage.general['counter'] += 1
    counter_label.set_text(f"Count: {app.storage.general['counter']}")

counter_label = ui.label(f"Count: {app.storage.general['counter']}")
ui.button('Increment', on_click=increment)
```

### User State with Persistence

```python
from nicegui import ui, app

# User preferences (persists across sessions)
if 'theme' not in app.storage.user:
    app.storage.user['theme'] = 'light'

def toggle_theme():
    app.storage.user['theme'] = 'dark' if app.storage.user['theme'] == 'light' else 'light'
    ui.notify(f"Theme: {app.storage.user['theme']}")

ui.button('Toggle Theme', on_click=toggle_theme)
ui.label(f"Current theme: {app.storage.user['theme']}")
```

### Reactive Components

```python
from nicegui import ui

data = {'items': ['A', 'B', 'C']}

@ui.refreshable
def item_list():
    for item in data['items']:
        ui.label(item)

def add_item():
    data['items'].append(f'New {len(data["items"]) + 1}')
    item_list.refresh()

item_list()
ui.button('Add Item', on_click=add_item)
```

---

## Async Operations

### Background Task

```python
from nicegui import ui, background_tasks
import asyncio

progress = ui.linear_progress(0).props('instant-feedback')
status = ui.label('Ready')

async def long_task():
    status.set_text('Working...')
    progress.value = 0

    for i in range(10):
        await asyncio.sleep(0.5)
        progress.value = (i + 1) / 10

    status.set_text('Complete!')
    ui.notify('Task finished')

def start_task():
    background_tasks.create(long_task())

ui.button('Start Task', on_click=start_task)
```

### Debounced Input

```python
from nicegui import ui
import asyncio

search_result = ui.label()
task = None

async def do_search(value):
    await asyncio.sleep(0.3)  # Debounce delay
    search_result.set_text(f'Search results for: {value}')

def on_search(e):
    global task
    if task:
        task.cancel()
    task = background_tasks.create(do_search(e.value))

ui.input('Search', on_change=on_search)
search_result
```

---

## Styling Patterns

### Responsive Grid

```python
from nicegui import ui

# 1 column on mobile, 2 on tablet, 3 on desktop
with ui.element('div').classes('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'):
    for i in range(6):
        with ui.card():
            ui.label(f'Card {i+1}').classes('text-h6')
            ui.label('Card content here')
```

### Dark Mode Support

```python
from nicegui import ui, app

# Dark mode toggle
def toggle_dark():
    dark = app.storage.user.get('dark', False)
    app.storage.user['dark'] = not dark
    ui.dark_mode(not dark)

# Apply on load
ui.dark_mode(app.storage.user.get('dark', False))

ui.button('Toggle Dark Mode', on_click=toggle_dark)
```

### Custom Card Styles

```python
from nicegui import ui

# Hover effect card
with ui.card().classes('''
    w-64
    transition-all
    duration-300
    hover:-translate-y-2
    hover:shadow-xl
    cursor-pointer
''') as card:
    ui.image('https://picsum.photos/300/200').classes('w-full')
    ui.label('Hover Card').classes('text-h6 p-4')

    card.on_click(lambda: ui.notify('Card clicked!'))

# Gradient card
with ui.card().classes('w-64 bg-gradient-to-br from-blue-500 to-purple-600 text-white'):
    ui.label('Gradient Card').classes('text-h6')
    ui.label('With gradient background')
```

---

## Error Handling

### Try-Catch in Events

```python
from nicegui import ui

def risky_operation():
    try:
        # Potentially failing operation
        result = 1 / 0
        ui.notify(f'Result: {result}')
    except ZeroDivisionError:
        ui.notify('Cannot divide by zero!', type='negative')
    except Exception as e:
        ui.notify(f'Error: {str(e)}', type='negative')

ui.button('Risky Operation', on_click=risky_operation)
```

### Loading State Pattern

```python
from nicegui import ui

btn = ui.button('Submit')
status = ui.label()

async def submit():
    btn.props('loading')
    btn.disable()
    status.set_text('Processing...')

    try:
        # Do work
        await asyncio.sleep(2)
        ui.notify('Success!', type='positive')
    except Exception as e:
        ui.notify(f'Failed: {e}', type='negative')
    finally:
        btn.props('loading=false')
        btn.enable()
        status.set_text('')

btn.on_click(submit)
```

### Global Error Handler

```python
from nicegui import ui, app

@app.exception_handler
async def handle_exception(request, exc):
    ui.notify(f'An error occurred: {exc}', type='negative', position='top')
    return {'message': str(exc)}
```

---

## Performance Tips

1. **Use `run.cpu_bound()` for heavy computations**
2. **Use `ui.refreshable` for dynamic content instead of clearing and rebuilding**
3. **Use `bind_` methods for automatic updates instead of manual refresh**
4. **Limit `ui.timer()` frequency**
5. **Use pagination for large tables**
6. **Lazy load heavy components**

---

## Quick Snippets

### Confirm Dialog

```python
def confirm_action():
    with ui.dialog() as dialog, ui.card():
        ui.label('Are you sure?').classes('text-h6')
        with ui.row():
            ui.button('No', on_click=dialog.close)
            ui.button('Yes', on_click=lambda: [dialog.close(), do_action()])
    dialog.open()
```

### Copy to Clipboard

```python
ui.button('Copy', on_click=lambda: ui.run_javascript('navigator.clipboard.writeText("text")'))
```

### Open External Link

```python
ui.button('Open', on_click=lambda: ui.run_javascript('window.open("https://example.com")'))
```

### File Download

```python
from nicegui import ui
from io import StringIO

def download():
    buffer = StringIO()
    buffer.write('Hello, World!')
    ui.download(buffer.getvalue(), 'hello.txt')

ui.button('Download', on_click=download)
```

---

*For more details, see the main SKILL.md file.*
