# NiceGUI Styling Guide

Complete reference for styling NiceGUI applications using Tailwind CSS and Quasar props.

## Table of Contents

- [Styling Hierarchy](#styling-hierarchy)
- [Tailwind CSS](#tailwind-css)
- [Quasar Props](#quasar-props)
- [Quasar Typography Classes](#quasar-typography-classes)
- [Color System](#color-system)
- [Common Patterns](#common-patterns)
- [Responsive Design](#responsive-design)
- [Dark Mode](#dark-mode)

---

## Styling Hierarchy

NiceGUI applies styles in this order (later overrides earlier):

```python
# 1. Element kwargs (built-in)
ui.button('OK', color='primary', flat=True, size='sm')

# 2. Tailwind CSS classes (RECOMMENDED)
ui.button('OK').classes('bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg')

# 3. Quasar props (Vue component properties)
ui.button('OK').props('outline rounded dense no-caps')

# 4. Inline styles
ui.button('OK').style('font-size: 16px; text-transform: none')

# 5. Global CSS (affects all pages)
ui.add_css('''
    .custom-button { font-size: 16px; }
''')
```

---

## Tailwind CSS

NiceGUI includes Tailwind CSS by default. Use `.classes()` to apply Tailwind utility classes.

### Layout

| Category | Classes | Description |
| ---------- | --------- | ------------- |
| **Display** | `flex`, `inline-flex`, `grid`, `block`, `inline`, `hidden` | Display mode |
| **Flex Direction** | `flex-row`, `flex-col`, `flex-row-reverse`, `flex-col-reverse` | Direction |
| **Flex Wrap** | `flex-wrap`, `flex-nowrap`, `flex-wrap-reverse` | Wrapping |
| **Justify** | `justify-start`, `justify-center`, `justify-end`, `justify-between`, `justify-around`, `justify-evenly` | Horizontal alignment |
| **Align Items** | `items-start`, `items-center`, `items-end`, `items-stretch`, `items-baseline` | Vertical alignment |
| **Align Content** | `content-start`, `content-center`, `content-end`, `content-between`, `content-around` | Multi-line alignment |

### Spacing

```python
# Padding
p-0, p-1, p-2, p-3, p-4, p-5, p-6, p-8, p-10, p-12  # All sides
px-4  # Horizontal (left + right)
py-4  # Vertical (top + bottom)
pt-4, pb-4, pl-4, pr-4  # Individual sides

# Margin
m-0, m-1, m-2, m-4, m-6, m-8, m-12, m-auto
mx-4, my-4, mt-4, mb-4, ml-4, mr-4

# Gap (for flex/grid containers)
gap-0, gap-1, gap-2, gap-4, gap-6, gap-8
gap-x-4, gap-y-4
```

### Sizing

```python
# Width
w-0, w-1, w-2, w-4, w-8, w-12, w-16, w-20, w-24, w-32, w-48, w-64
w-full      # 100%
w-screen    # 100vw
w-auto
w-1/2, w-1/3, w-1/4, w-2/3, w-3/4  # Fractions
min-w-0, min-w-full
max-w-0, max-w-full, max-w-xs, max-w-sm, max-w-md, max-w-lg, max-w-xl

# Height
h-0, h-1, h-2, h-4, h-8, h-12, h-16, h-20, h-24, h-32, h-48, h-64
h-full, h-screen, h-auto
min-h-0, min-h-full, min-h-screen
max-h-0, max-h-full, max-h-screen
```

### Colors (Background)

```python
# Format: bg-{color}-{shade}
bg-white, bg-black
bg-gray-50, bg-gray-100, bg-gray-200, bg-gray-300, bg-gray-400,
bg-gray-500, bg-gray-600, bg-gray-700, bg-gray-800, bg-gray-900

bg-red-500, bg-blue-500, bg-green-500, bg-yellow-500
bg-purple-500, bg-pink-500, bg-indigo-500

# Opacity
bg-white/50, bg-black/25  # 50%, 25% opacity
```

### Colors (Text)

```python
# Format: text-{color}-{shade}
text-white, text-black
text-gray-500, text-red-500, text-blue-500, text-green-500
text-transparent

# Opacity
text-white/75
```

### Colors (Border)

```python
# Format: border-{color}-{shade}
border-white, border-gray-200, border-red-500

# Border width
border, border-0, border-2, border-4, border-8
border-t, border-b, border-l, border-r

# Border style
border-solid, border-dashed, border-dotted

# Border radius
rounded-none, rounded-sm, rounded, rounded-md, rounded-lg, rounded-xl
rounded-2xl, rounded-3xl, rounded-full
rounded-t-lg, rounded-b-lg, rounded-l-lg, rounded-r-lg
```

### Typography

```python
# Font size
text-xs, text-sm, text-base, text-lg, text-xl
text-2xl, text-3xl, text-4xl, text-5xl, text-6xl, text-7xl, text-8xl, text-9xl

# Font weight
font-thin, font-extralight, font-light, font-normal
font-medium, font-semibold, font-bold, font-extrabold, font-black

# Text alignment
text-left, text-center, text-right, text-justify

# Text color (see Colors section)
text-white, text-gray-500, text-red-500

# Text decoration
underline, overline, line-through, no-underline

# Text transform
uppercase, lowercase, capitalize, normal-case

# Letter spacing
tracking-tighter, tracking-tight, tracking-normal, tracking-wide, tracking-wider, tracking-widest

# Line height
leading-none, leading-tight, leading-snug, leading-normal, leading-relaxed, leading-loose
```

### Effects

```python
# Shadow
shadow-none, shadow-sm, shadow, shadow-md, shadow-lg, shadow-xl, shadow-2xl, shadow-inner

# Opacity
opacity-0, opacity-25, opacity-50, opacity-75, opacity-100

# Blur
blur-none, blur-sm, blur, blur-md, blur-lg, blur-xl, blur-2xl, blur-3xl

# Transition
transition-none, transition-all, transition-colors, transition-opacity
transition-shadow, transition-transform, transition-[property]

# Duration
duration-75, duration-100, duration-150, duration-200, duration-300, duration-500, duration-700, duration-1000

# Ease
ease-linear, ease-in, ease-out, ease-in-out

# Transform (hover/focus states)
hover:scale-110, hover:scale-105, hover:scale-95
hover:rotate-45, hover:rotate-90
hover:translate-x-2, hover:translate-y-2
hover:-translate-y-1
hover:shadow-lg, hover:shadow-xl
hover:bg-blue-600, hover:text-white
hover:border-blue-500

# Cursor
cursor-auto, cursor-default, cursor-pointer, cursor-wait
cursor-text, cursor-move, cursor-not-allowed
```

### Z-Index

```python
z-0, z-10, z-20, z-30, z-40, z-50, z-auto
```

### Overflow

```python
overflow-auto, overflow-hidden, overflow-visible, overflow-scroll
overflow-x-auto, overflow-y-auto
overflow-x-hidden, overflow-y-hidden
```

---

## Quasar Props

Use `.props()` to add Quasar Framework component properties.

### Button Props

```python
# Style
ui.button('OK').props('flat')           # No background
ui.button('OK').props('outline')        # Border only
ui.button('OK').props('bordered')       # Add border to filled
ui.button('OK').props('unelevated')     # No shadow
ui.button('OK').props('rounded')        # Pill shape
ui.button('OK').props('push')            # Push effect
ui.button('OK').props('glossy')         # Glossy sheen
ui.button('OK').props('dense')           # Compact size
ui.button('OK').props('fab')             # Floating action style
ui.button('OK').props('square')          # No border radius
ui.button('OK').props('round')           # Circular (icon buttons)

# State
ui.button('OK').props('disable')
ui.button('OK').props('loading')
ui.button('OK').props('no-caps')         # Disable uppercase
ui.button('OK').props('no-wrap')         # Disable text wrapping
```

### Input Props

```python
# Style
ui.input('Label').props('outlined')       # Border around input
ui.input('Label').props('filled')         # Filled background
ui.input('Label').props('standout')       # Prominent filled
ui.input('Label').props('borderless')    # No bottom border
ui.input('Label').props('rounded')        # Rounded corners
ui.input('Label').props('square')         # No border radius
ui.input('Label').props('dense')          # Compact height

# Behavior
ui.input('Label').props('clearable')      # Show clear button
ui.input('Label').props('readonly')
ui.input('Label').props('disable')
ui.input('Label').props('autofocus')
ui.input('Label').props('loading')

# Types
ui.input('Label').props('type=password')
ui.input('Label').props('type=email')
ui.input('Label').props('type=number')
ui.input('Label').props('type=search')
ui.input('Label').props('type=tel')
ui.input('Label').props('type=url')
ui.input('Label').props('type=textarea')
```

### Card Props

```python
ui.card().props('flat')                   # No shadow
ui.card().props('bordered')               # Add border
ui.card().props('square')                  # No border radius
```

### Dialog Props

```python
with ui.dialog() as dialog:
    dialog.props('maximized')             # Full screen
    dialog.props('persistent')            # Can't close by clicking outside
    dialog.props('full-width')              # Full width
    dialog.props('no-esc-dismiss')        # Can't close with ESC
    dialog.props('no-backdrop-dismiss')   # Can't close clicking backdrop
    dialog.props('auto-close')              # Auto close on action
    dialog.props('seamless')                # No backdrop
```

### Menu Props

```python
ui.menu().props('auto-close')             # Close on item selection
ui.menu().props('fit')                    # Fit to anchor width
ui.menu().props('cover')                  # Cover anchor element
ui.menu().props('anchor=bottom left')     # Position
ui.menu().props('self=top left')
```

### Header/Footer/Drawer Props

```python
ui.header().props('bordered')             # Add border
ui.header().props('elevated')             # Add shadow
ui.header().props('reveal')               # Show/hide on scroll
```

### Table Props

```python
ui.table().props('flat')                  # No card style
ui.table().props('bordered')              # Add borders
ui.table().props('dense')                 # Compact rows
ui.table().props('wrap-cells')            # Wrap cell content
ui.table().props('hide-header')           # Hide header row
ui.table().props('hide-pagination')       # Hide pagination
ui.table().props('hide-bottom')           # Hide bottom area
ui.table().props('grid')                  # Grid mode (mobile)
```

---

## Quasar Typography Classes

These are built-in Quasar classes available via `.classes()`:

```python
# Headings
.text-h1   # Light 96px, -1.5px letter-spacing
.text-h2   # Light 60px, -0.5px letter-spacing
.text-h3   # Normal 48px, 0 letter-spacing
.text-h4   # Normal 34px, 0.25px letter-spacing
.text-h5   # Normal 24px, 0 letter-spacing
.text-h6   # Medium 20px, 0.15px letter-spacing

# Subtitles
.text-subtitle1   # Normal 16px, 0.15px letter-spacing
.text-subtitle2   # Medium 14px, 0.1px letter-spacing

# Body
.text-body1   # Normal 16px, 0.5px letter-spacing
.text-body2   # Normal 14px, 0.25px letter-spacing

# Other
.text-caption   # Normal 12px, 0.4px letter-spacing
.text-overline  # Normal 10px, 1.5px letter-spacing, uppercase

# Weights (within Quasar)
.text-weight-thin
.text-weight-light
.text-weight-regular
.text-weight-medium
.text-weight-bold
.text-weight-bolder
```

---

## Color System

### Quasar Brand Colors

```python
# Built-in brand colors (use with .classes() or element kwargs)
'primary', 'secondary', 'accent'
'positive', 'negative', 'warning', 'info', 'dark'

# Usage
ui.button('OK', color='primary')
ui.button('Delete', color='negative')
ui.label('Success').classes('text-positive')
ui.card().classes('bg-dark text-white')
```

### Custom Theme Colors

```python
from nicegui import ui

# Set custom theme colors
ui.colors(
    primary='#1976D2',
    secondary='#26A69A',
    accent='#9C27B0',
    positive='#21BA45',
    negative='#C10015',
    warning='#F2C037',
    info='#31CCEC',
    dark='#1D1D1D'
)
```

### Tailwind Color Palette

```python
# Grays
bg-gray-50   # #F9FAFB
bg-gray-100  # #F3F4F6
bg-gray-200  # #E5E7EB
bg-gray-300  # #D1D5DB
bg-gray-400  # #9CA3AF
bg-gray-500  # #6B7280
bg-gray-600  # #4B5563
bg-gray-700  # #374151
bg-gray-800  # #1F2937
bg-gray-900  # #111827

# Reds (error/negative)
bg-red-50, bg-red-100 ... bg-red-900

# Greens (success/positive)
bg-green-50, bg-green-100 ... bg-green-900

# Blues (info)
bg-blue-50, bg-blue-100 ... bg-blue-900

# Yellows (warning)
bg-yellow-50, bg-yellow-100 ... bg-yellow-900
```

---

## Common Patterns

### Card Styles

```python
# Standard elevated card
with ui.card():
    ui.label('Content')

# Flat bordered card
with ui.card().props('flat bordered'):
    ui.label('Flat Card')

# Hover lift effect
with ui.card().classes('transition-all hover:-translate-y-1 hover:shadow-lg'):
    ui.label('Hover me')

# Responsive card
with ui.card().classes('w-full max-w-md mx-auto'):
    ui.label('Responsive')
```

### Button Styles

```python
# Primary action
ui.button('Save', color='primary')

# Secondary action
ui.button('Cancel')

# Destructive action
ui.button('Delete', color='negative')

# Icon button
ui.icon_button('edit', color='primary')

# Outlined button
ui.button('Outlined').props('outline')

# Loading state
btn = ui.button('Processing')
btn.props('loading')
```

### Form Layouts

```python
# Vertical form with spacing
with ui.column().classes('gap-4 w-full'):
    ui.input('Name').classes('w-full')
    ui.input('Email').classes('w-full')
    ui.select(['A', 'B'], label='Type').classes('w-full')
    with ui.row().classes('justify-end'):
        ui.button('Submit', color='primary')

# Two-column form
with ui.row().classes('gap-4 w-full'):
    with ui.column().classes('flex-1'):
        ui.input('First Name')
    with ui.column().classes('flex-1'):
        ui.input('Last Name')

# Centered form
with ui.element('div').classes('flex justify-center items-center min-h-screen'):
    with ui.card().classes('w-full max-w-md p-6'):
        ui.label('Login').classes('text-h5 text-center')
        # ... form fields
```

### Table Styling

```python
# Full-width table
ui.table(...).classes('w-full')

# Striped rows
ui.table(...).classes('table-striped')

# Hover effect
ui.table(...).classes('table-hover')

# Dense rows
ui.table(...).props('dense')

# Bordered cells
ui.table(...).props('bordered')
```

---

## Responsive Design

### Breakpoints

```python
# Tailwind breakpoints (mobile-first)
sm: 640px    # @media (min-width: 640px)
md: 768px    # @media (min-width: 768px)
lg: 1024px   # @media (min-width: 1024px)
xl: 1280px   # @media (min-width: 1280px)
2xl: 1536px  # @media (min-width: 1536px)

# Usage (mobile-first approach)
with ui.element('div').classes('w-full md:w-1/2 lg:w-1/3'):
    # Full width on mobile, half on tablet, third on desktop
```

### Responsive Patterns

```python
# Responsive grid
with ui.element('div').classes('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'):
    for i in range(6):
        ui.card()

# Responsive flex direction
with ui.element('div').classes('flex flex-col md:flex-row gap-4'):
    ui.card().classes('flex-1')
    ui.card().classes('flex-1')

# Hide on mobile
ui.label('Desktop only').classes('hidden md:block')

# Show only on mobile
ui.label('Mobile only').classes('md:hidden')

# Responsive padding
with ui.card().classes('p-4 md:p-6 lg:p-8'):
    pass

# Responsive text size
ui.label('Responsive text').classes('text-lg md:text-xl lg:text-2xl')
```

### Container Queries (Alternative)

```python
# Use max-width containers
with ui.card().classes('w-full max-w-xs'):   # Mobile
    pass
with ui.card().classes('w-full max-w-md'):   # Tablet
    pass
with ui.card().classes('w-full max-w-4xl'): # Desktop
    pass
```

---

## Dark Mode

### Automatic Dark Mode

```python
from nicegui import ui, app

# Toggle dark mode
def toggle_dark():
    is_dark = ui.dark_mode().value
    ui.dark_mode(not is_dark)

ui.button('Toggle Dark Mode', on_click=toggle_dark)
```

### Manual Dark Mode

```python
from nicegui import ui

# Enable dark mode
ui.dark_mode(True)

# Disable dark mode
ui.dark_mode(False)
```

### Dark Mode Aware Styling

```python
# Use dark: prefix for dark mode variants
ui.label('Text').classes('text-gray-900 dark:text-white')
ui.card().classes('bg-white dark:bg-gray-800')

# Conditional classes based on mode
def get_card_classes():
    return 'bg-white text-gray-900' if not is_dark else 'bg-gray-800 text-white'
```

### Persistent Dark Mode

```python
from nicegui import ui, app

# Store preference
@app.on_connect
async def on_connect():
    if 'dark_mode' in app.storage.user:
        ui.dark_mode(app.storage.user['dark_mode'])

def toggle():
    current = ui.dark_mode().value
    ui.dark_mode(not current)
    app.storage.user['dark_mode'] = not current
```

---

## Helper Functions

### Utility for Common Patterns

```python
def styled_card(title: str, **kwargs):
    """Create a consistently styled card."""
    with ui.card().classes('w-full').props('flat bordered') as card:
        if title:
            ui.label(title).classes('text-h6 mb-4')
        return card

def primary_button(text: str, on_click=None):
    """Create a primary action button."""
    return ui.button(text, on_click=on_click, color='primary')

def danger_button(text: str, on_click=None):
    """Create a danger/destructive button."""
    return ui.button(text, on_click=on_click, color='negative')

# Usage
with styled_card('User Information'):
    ui.input('Name')
    with ui.row().classes('justify-end gap-2'):
        danger_button('Cancel')
        primary_button('Save')
```

---

*For element-specific styling, see [elements.md](elements.md)*
