# VidSnapAI Project Memory

## Architecture
- **Stack**: Flask (Python) + Jinja2 templates + Vanilla JS
- **Entry**: `main.py` — all routes + API endpoints
- **Templates**: `templates/` — base.html, index.html, create.html, gallery.html, about.html, features.html
- **Static CSS**: `static/css/` — style.css (global), common.css, create.css, gallery.css, about.css, features.css, responsive.css
- **Static JS**: `static/js/` — theme.js, notifications.js, shortcuts.js, create.js, dragdrop.js, gallery.js, preview.js

## Design System
- **Theme**: Red + Black (primary), Gold theme toggle via `[data-theme="gold"]`
- **Font**: Inter (Google Fonts) loaded in base.html
- **Accent**: `var(--accent-color)` = #ff0000, gradient via `var(--gradient-brand)`
- **CSS variables** defined in `:root` and `[data-theme="gold"]` in style.css
- **AOS** (Animate On Scroll) loaded in base.html via CDN, initialized in inline script

## Key Decisions (UI Upgrade 2025-03)
- Sticky blur navbar: `.navbar-premium` with `backdrop-filter: blur(20px)`
- Active nav indicator: JS highlights `.nav-link-premium.active` by path
- Animated upload zone: CSS `@property --angle` + conic-gradient rotation
- All cards use glassmorphism: `background: rgba(255,255,255,0.04); backdrop-filter: blur(16px)`
- Purple (#8b5cf6) was a bug in about.css — corrected to red (#ff0000) for `.team-role` and `.social-link`
- Gallery share modal was outside `{% block content %}` → fixed (moved inside block)
- Duplicate `#fullscreenModal` removed from gallery.html

## Known Issues / Notes
- `preview.js` targets `#preview-audio-btn` but create.html uses `#previewAudioBtn` — unused file
- `config.py` has hardcoded ElevenLabs API key (not a UI concern)
- Gallery titles show raw UUID filenames (cosmetic, not changed — backend concern)
