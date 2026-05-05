# UI Template (PyQt6)

A modular and scalable desktop UI skeleton built with PyQt6.

Main goals of this template:
- Feature-based growth
- Centralized theme management (light/dark)
- Reusable layout and widget architecture
- Simple yet professional UI foundation

## Features

- Page navigation based on `QStackedWidget`
- Sidebar + Topbar + Content shell architecture
- Light/dark theme switching with `ThemeManager`
- QSS layer separation for `core / light / dark`
- Theme-aware icon resolution (`name.svg`, `name-dark.svg`)
- Reusable `ViewLayout` and `AppButton`

## Project Structure

```text
app
├── assets
│   ├── fonts
│   └── icons
├── core
│   ├── constant
│   │   └── app_constant.py
│   ├── router
│   │   ├── __init__.py
│   │   └── router.py
│   ├── services
│   │   └── uart 
│   └── theme
│       ├── __init__.py
│       └── theme.py
├── feature
│   └── home
│       ├── core
│       │   ├── home.py
│       │   └── states.py
│       ├── view
│       │   └── home_view.py
│       ├── widget
│       │   └── __init__.py
│       └── __init__.py
├── layouts
│   ├── footer.py
│   ├── main_layout.py
│   ├── sidebar.py
│   ├── topbar.py
│   └── view_layout.py
├── style
│   ├── core
│   ├── dark
│   └── light
├── widgets
│   ├── button.py
│   ├── pill_divider.py
│   └── theme_switch.py
└── main_window.py

main.py

notes:
    - fonts: not currently used
    - uart: planned for future
```

## Running the App

> Example for Windows / PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install PyQt6
py .\main.py
```

## Application Flow

1. `main.py` creates the `QApplication`.
2. `ThemeManager(app)` is started and applies the saved theme (`QSettings`).
3. `MainWindow` is launched.
4. Inside `MainLayout`:
   - `Sidebar`
   - `QStackedWidget`
   are initialized together.
5. Views from Router are added to the stack.
6. When a route is selected from the Sidebar, the active page changes.

## Theme Architecture

The theme system is managed in `app/core/theme/theme.py`.

- `Theme`: `LIGHT`, `DARK`
- `StyleModule`: `BUTTON`, `SIDEBAR_BUTTON`, `SURFACE`
- Loading order: for each module **core -> selected theme**

This allows:
- Structural/style rules (like shape/size) to come from a single place (`core`)
- Color/palette rules to live in theme files (`light`/`dark`)

### Layer Rule

- `core/*.qss`:
  - border width/style
  - radius
  - spacing / size
  - structural behavior for states
- `light/*.qss` and `dark/*.qss`:
  - `background-color`
  - `color`
  - `border-color`
  - state colors per theme

## Layout Architecture

### `ViewLayout` (`app/layouts/view_layout.py`)

Common shell for all pages:
- Topbar
- Divider (pill line widget)
- Main content container (`ViewMainContent`)

Defines shared look/layout standards here.

### `Sidebar` (`app/layouts/sidebar.py`)

Three-section structure:
- Header
- Scrollable nav
- Footer

Route list is provided by `router.get_sidebar_routes()`.

## Navigation

Router in `app/core/router/router.py` contains:
- Route enum
- Sidebar route metadata
- Lazy view factory

Switch active page with `MainLayout.show_page(route_value)`.

## Reusable Widgets

### `AppButton`

`app/widgets/button.py`:
- Variants (`standard`, `ghost`, `primary`)
- Contexts (`sidebar`, `page`, etc.)
- Theme-aware icon support
- QSS targeting via dynamic property

### `Theme Switch`

`app/widgets/theme_switch.py`:
- Dynamic icon switching (`light` / `dark`)
- Triggers theme change with `toggled`
- Syncs UI state to current theme with `sync_checked()`
- Smooth transition feel with shrink/grow animation

### `PillDivider`

`app/widgets/pill_divider.py`:
- Custom drawing via `paintEvent`
- Anti-aliased rounded divider
- Runtime color update on theme change

## Adding a New View

1. Create `app/feature/<name>/view/<name>_view.py`
2. Subclass from `ViewLayout`:

```python
from app.layouts.view_layout import ViewLayout
class SettingsView(ViewLayout):
    def __init__(self):
        super().__init__(title="Settings")
```

3. In `router.py`:
   - Add route to enum
   - Add a route factory
   - Add title/icon to sidebar route list

4. Optionally, define custom QSS selectors for the feature in a separate file.

## Icon Rule

`ThemeManager.resolve_icon_path()` uses the following fallback logic:
- In dark theme, first tries `name-dark.svg`
- Then `name.svg`
- Then `name.png`

Icons are stored under `app/assets/icons`.

## Development Notes

- For UI experiments, test directly via `main.py`.
- Don't create `QWidget` before `QApplication` is created.
- In QSS, keep selector names aligned with `objectName` / dynamic property.
- If you add a new QSS module, don't forget to add it to the `StyleModule` enum.


---

This template is designed to balance rapid startup with long-term, orderly growth.
