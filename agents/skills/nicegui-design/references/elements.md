# NiceGUI Elements Reference

Complete catalog of NiceGUI UI elements with descriptions and common use cases.

## Table of Contents

- [Layout Elements](#layout-elements)
- [Input Elements](#input-elements)
- [Display Elements](#display-elements)
- [Data Elements](#data-elements)
- [Interactive Elements](#interactive-elements)
- [Charts & Visualization](#charts--visualization)
- [Advanced Elements](#advanced-elements)
- [3D & Media](#3d--media)

______________________________________________________________________

## Layout Elements

### Containers

| Element               | Description                    | Key Props/Classes                     |
| --------------------- | ------------------------------ | ------------------------------------- |
| `ui.card()`           | Elevated container with shadow | `flat`, `bordered`, `square`          |
| `ui.column()`         | Vertical flex layout           | `items-center`, `justify-center`      |
| `ui.row()`            | Horizontal flex layout         | `wrap`, `items-center`, `gap-4`       |
| `ui.expansion()`      | Collapsible section            | `caption`, `group`, `icon`            |
| `ui.tabs()`           | Tabbed interface               | `vertical`, `no-caps`                 |
| `ui.tab_panels()`     | Content panels for tabs        | -                                     |
| `ui.splitter()`       | Resizable split panes          | `horizontal`, `limits`, `before_slot` |
| `ui.scroll_area()`    | Scrollable container           | `height`, `width`                     |
| `ui.virtual_scroll()` | Efficient large list scrolling | -                                     |

### Page Structure

| Element             | Description            | Key Props                                 |
| ------------------- | ---------------------- | ----------------------------------------- |
| `ui.header()`       | Top app bar            | `reveal`, `bordered`, `elevated`          |
| `ui.footer()`       | Bottom bar             | `reveal`, `bordered`                      |
| `ui.left_drawer()`  | Left sidebar           | `value`, `reveal`, `bordered`, `elevated` |
| `ui.right_drawer()` | Right sidebar          | Same as left_drawer                       |
| `ui.page_sticky()`  | Fixed position element | `position` (top-right, bottom-left, etc.) |
| `ui.element()`      | Generic container      | `tag` (div, span, section, etc.)          |

### Navigation

| Element             | Description          | Key Props                             |
| ------------------- | -------------------- | ------------------------------------- |
| `ui.link()`         | Hyperlink            | `new_tab`, `target`                   |
| `ui.button_group()` | Grouped buttons      | `value`, `outline`, `flat`            |
| `ui.breadcrumbs()`  | Navigation path      | -                                     |
| `ui.pagination()`   | Page navigation      | `min`, `max`, `direction_links`       |
| `ui.stepper()`      | Wizard/multi-step    | `vertical`, `animated`, `flat`        |
| `ui.timeline()`     | Chronological events | `side` (left, right)                  |
| `ui.tree()`         | Hierarchical tree    | `nodes`, `label_key`, `tick_strategy` |
| `ui.carousel()`     | Content slider       | `arrows`, `navigation`, `autoplay`    |

______________________________________________________________________

## Input Elements

### Text Input

| Element           | Description              | Key Props                                                     |
| ----------------- | ------------------------ | ------------------------------------------------------------- |
| `ui.input()`      | Single-line text         | `label`, `placeholder`, `password`, `clearable`, `validation` |
| `ui.number()`     | Numeric input            | `min`, `max`, `precision`, `prefix`, `suffix`, `format`       |
| `ui.textarea()`   | Multi-line text          | `autogrow`, `clearable`                                       |
| `ui.editor()`     | Rich text editor (Quill) | `toolbar`, `placeholder`                                      |
| `ui.codemirror()` | Code editor              | `language`, `theme`, `indentation`                            |

### Selection

| Element         | Description           | Key Props                                                     |
| --------------- | --------------------- | ------------------------------------------------------------- |
| `ui.select()`   | Dropdown              | `options`, `label`, `multiple`, `clearable`, `new_value_mode` |
| `ui.slider()`   | Range slider          | `min`, `max`, `step`, `label`, `reverse`                      |
| `ui.range()`    | Dual-handle range     | `min`, `max`, `step`                                          |
| `ui.knob()`     | Circular input        | `min`, `max`, `show_value`, `angle`                           |
| `ui.radio()`    | Single selection      | `options`, `value`                                            |
| `ui.toggle()`   | Button-style toggle   | `options`, `clearable`, `multiple`                            |
| `ui.checkbox()` | Boolean checkbox      | `value`                                                       |
| `ui.switch()`   | Boolean toggle switch | `value`, `color`                                              |

### Date & Time

| Element             | Description             | Key Props                                |
| ------------------- | ----------------------- | ---------------------------------------- |
| `ui.date()`         | Date picker             | `mask`, `range`, `multiple`, `today_btn` |
| `ui.time()`         | Time picker             | `mask`, `with_seconds`, `format24h`      |
| `ui.color_picker()` | Color picker            | `value` (hex, rgb, rgba)                 |
| `ui.color_input()`  | Color input with picker | `label`, `value`, `clearable`            |

### File Handling

| Element         | Description           | Key Props                                         |
| --------------- | --------------------- | ------------------------------------------------- |
| `ui.file()`     | File path input       | `directory`, `multiple`                           |
| `ui.upload()`   | File upload widget    | `label`, `multiple`, `max_file_size`, `on_upload` |
| `ui.download()` | Trigger file download | `src` (path or bytes)                             |

______________________________________________________________________

## Display Elements

### Text & Content

| Element             | Description        | Key Props                                 |
| ------------------- | ------------------ | ----------------------------------------- |
| `ui.label()`        | Text display       | -                                         |
| `ui.html()`         | Raw HTML content   | `tag` (div, span, etc.)                   |
| `ui.markdown()`     | Markdown rendering | `extras` (tables, code highlighting)      |
| `ui.mermaid()`      | Diagram rendering  | `content` (mermaid syntax)                |
| `ui.katex()`        | Math rendering     | `expression` (LaTeX)                      |
| `ui.code()`         | Code block display | `language`                                |
| `ui.badge()`        | Status indicator   | `color`, `floating`, `transparent`        |
| `ui.chip()`         | Tag/pill display   | `icon`, `color`, `removable`, `clickable` |
| `ui.tooltip()`      | Hover tooltip      | `text`, `delay`, `position`               |
| `ui.notification()` | Toast notification | `type`, `position`, `timeout`, `closeBtn` |
| `ui.notify()`       | Quick toast        | `message`, `type`, `position`             |

### Media

| Element                  | Description            | Key Props                                       |
| ------------------------ | ---------------------- | ----------------------------------------------- |
| `ui.image()`             | Image display          | `src`, `fit` (cover, contain, fill)             |
| `ui.interactive_image()` | Image with annotations | `src`, `cross`, `events`                        |
| `ui.avatar()`            | User avatar            | `icon`, `color`, `size`, `font-size`            |
| `ui.icon()`              | Material icon          | `name`, `color`, `size`                         |
| `ui.audio()`             | Audio player           | `src`, `controls`, `autoplay`, `loop`           |
| `ui.video()`             | Video player           | `src`, `controls`, `autoplay`, `loop`, `poster` |
| `ui.skeleton()`          | Loading placeholder    | `type` (text, rect, circle), `animation`        |
| `ui.spinner()`           | Loading indicator      | `type`, `size`, `color`                         |

### Progress & Status

| Element                  | Description             | Key Props                           |
| ------------------------ | ----------------------- | ----------------------------------- |
| `ui.linear_progress()`   | Horizontal progress bar | `min`, `max`, `show_value`          |
| `ui.circular_progress()` | Circular progress       | `min`, `max`, `show_value`, `angle` |
| `ui.banner()`            | Top notification area   | `text`, `actions`                   |
| `ui.separator()`         | Visual divider          | `inset`, `vertical`, `spaced`       |
| `ui.space()`             | Flexible spacer         | -                                   |

______________________________________________________________________

## Data Elements

### Tables & Lists

| Element             | Description         | Key Props                                               |
| ------------------- | ------------------- | ------------------------------------------------------- |
| `ui.table()`        | Data table          | `columns`, `rows`, `row_key`, `selection`, `pagination` |
| `ui.aggrid()`       | Advanced data grid  | `options`, `html_columns`, `theme`                      |
| `ui.list()`         | Simple item list    | `separator`, `bordered`, `dense`                        |
| `ui.item()`         | List item           | `label`, `caption`, `section`                           |
| `ui.item_section()` | Section within item | `side`, `avatar`, `thumbnail`                           |
| `ui.item_label()`   | Label within item   | `lines`, `caption`, `header`                            |

### Data Editing

| Element            | Description     | Key Props                       |
| ------------------ | --------------- | ------------------------------- |
| `ui.json_editor()` | JSON editor     | `properties`, `schema`, `value` |
| `ui.grid()`        | CSS Grid layout | -                               |

______________________________________________________________________

## Interactive Elements

### Buttons & Actions

| Element              | Description            | Key Props                              |
| -------------------- | ---------------------- | -------------------------------------- |
| `ui.button()`        | Standard button        | `color`, `icon`, `on_click`, `loading` |
| `ui.icon_button()`   | Icon-only button       | `icon`, `color`, `on_click`            |
| `ui.fab()`           | Floating action button | `icon`, `color`, `on_click`            |
| `ui.fab_button()`    | FAB with label         | `icon`, `label`, `color`               |
| `ui.toggle_button()` | Toggle state button    | `value`, `on_change`                   |

### Menus & Dialogs

| Element             | Description      | Key Props                                        |
| ------------------- | ---------------- | ------------------------------------------------ |
| `ui.menu()`         | Dropdown menu    | `auto_close`, `fit`, `anchor`, `self`            |
| `ui.context_menu()` | Right-click menu | -                                                |
| `ui.dialog()`       | Modal dialog     | `value`, `persistent`, `maximized`, `full-width` |
| `ui.popup()`        | Popup container  | -                                                |

______________________________________________________________________

## Charts & Visualization

| Element          | Description          | Key Props                                   |
| ---------------- | -------------------- | ------------------------------------------- |
| `ui.pyplot()`    | Matplotlib figure    | `close` (auto-close figure)                 |
| `ui.plotly()`    | Plotly chart         | `figure`, `on_click`, `on_hover`            |
| `ui.echart()`    | Apache ECharts       | `options`, `on_point_click`, `theme`        |
| `ui.highchart()` | Highcharts           | `options`, `extras`, `on_point_click`       |
| `ui.line_plot()` | Real-time line chart | `limit`, `stroke`, `update_every`, `buffer` |

______________________________________________________________________

## Advanced Elements

### Reactive & Dynamic

| Element                  | Description              | Key Props                        |
| ------------------------ | ------------------------ | -------------------------------- |
| `ui.refreshable()`       | Auto-refresh component   | Decorator for dynamic content    |
| `ui.timer()`             | Periodic callback        | `interval`, `active`, `callback` |
| `ui.keyboard()`          | Keyboard events          | `on_key`, `active`, `ignore`     |
| `ui.bindable_property()` | Custom reactive property | `on_change`                      |

### Application

| Element          | Description            | Key Props                              |
| ---------------- | ---------------------- | -------------------------------------- |
| `ui.page()`      | Page decorator         | `path`, `title`, `favicon`, `dark`     |
| `ui.dark_mode()` | Toggle dark mode       | `value` (True/False)                   |
| `ui.colors()`    | Set theme colors       | `primary`, `secondary`, `accent`, etc. |
| `ui.query()`     | Query/selector utility | -                                      |

### Third-party Integrations

| Element          | Description         | Requirements          |
| ---------------- | ------------------- | --------------------- |
| `ui.leaflet()`   | Interactive maps    | `nicegui[ leaflet]`   |
| `ui.scene()`     | 3D scene (Three.js) | -                     |
| `ui.pinecone()`  | 3D point cloud      | -                     |
| `ui.aggrid()`    | AG Grid table       | `nicegui[aggrid]`     |
| `ui.plotly()`    | Plotly charts       | `nicegui[plotly]`     |
| `ui.echart()`    | Apache ECharts      | `nicegui[echarts]`    |
| `ui.highchart()` | Highcharts          | `nicegui[highcharts]` |

______________________________________________________________________

## 3D & Media

### 3D Scene (Three.js-based)

```python
with ui.scene(width=800, height=600) as scene:
    # Add objects
    scene.box(x=0, y=0, z=0, width=1, height=1, depth=1)
    scene.sphere(x=2, y=0, z=0, radius=0.5)
    scene.cylinder(x=-2, y=0, z=0, radius=0.5, height=2)

    # Add lights
    scene.point_light(x=0, y=2, z=0, color='white', intensity=1)
    scene.ambient_light(color='#333')
```

### Media Player Controls

```python
# Audio with controls
ui.audio('https://example.com/audio.mp3', controls=True, autoplay=False)

# Video player
ui.video('https://example.com/video.mp4', controls=True, poster='thumb.jpg')
```

______________________________________________________________________

## Element Method Reference

### Common Methods (Available on most elements)

| Method                 | Description                              |
| ---------------------- | ---------------------------------------- |
| `.classes()`           | Add Tailwind/CSS classes                 |
| `.style()`             | Add inline CSS                           |
| `.props()`             | Add Quasar component props               |
| `.bind_value()`        | Two-way bind to another element/property |
| `.on()`                | Add event handler                        |
| `.update()`            | Force UI update (usually automatic)      |
| `.mark()`              | Set marker for querying                  |
| `.run_method()`        | Call client-side method                  |
| `.get_computed_prop()` | Get client-side computed property        |

### Visibility Methods

```python
element.visible = False      # Hide
element.visible = True       # Show
element.classes('hidden')    # Via class
element.style('display: none')  # Via style
```

### Removal Methods

```python
element.clear()      # Remove children
element.delete()      # Remove element entirely
ui.remove(element)    # Alternative syntax
```

______________________________________________________________________

## Common Element Patterns

### Form Input with Validation

```python
name = ui.input('Name',
    validation={'Name required': lambda v: v and len(v) > 0}
)

email = ui.input('Email',
    validation={'Invalid email': lambda v: '@' in v if v else False}
)
```

### Dynamic Table with Actions

```python
columns = [
    {'name': 'name', 'label': 'Name', 'field': 'name'},
    {'name': 'actions', 'label': 'Actions', 'field': 'actions'},
]

table = ui.table(columns=columns, rows=rows, row_key='name')

for row in rows:
    with table.add_slot(f'body-cell-actions', row=row):
        ui.button('Edit', on_click=lambda r=row: edit(r))
```

### Responsive Grid

```python
with ui.grid().classes('grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'):
    for i in range(6):
        with ui.card():
            ui.label(f'Item {i}')
```

______________________________________________________________________

*For usage examples and patterns, see [common-patterns.md](common-patterns.md)*
