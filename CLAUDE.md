# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wagtail Shop Kit is an e-commerce starter built on Wagtail CMS 7.2 and Django 5.2. The project uses Docker for development and supports multiple databases (SQLite, PostgreSQL, MySQL).

## Essential Commands

### Quick Setup
```bash
make quickstart    # Full setup: build, up, migrate, collectstatic, test, run
make superuser     # Create admin user
```

### Docker Operations
```bash
make build         # Build Docker containers
make up            # Start containers
make down          # Stop containers
make restart       # Restart containers
make sh            # Open shell in container
```

### Development
```bash
make run           # Start Django dev server (in container)
make start         # Start frontend watch mode (SASS/JS)
make migrate       # Run database migrations
make test          # Run Django test suite
make collectstatic # Collect static files
```

### Frontend Assets
```bash
npm install        # Install dependencies
npm start          # Watch all assets (dev mode)
npm run build      # Build production assets
npm run styles:watch    # Watch SASS only
npm run scripts:watch   # Watch JS only
npm run images     # Optimize images
npm run clean      # Remove compiled assets
```

## Architecture

### Multi-Stage Docker Build
The project uses a two-stage Dockerfile:
1. **Node stage**: Compiles frontend assets (SASS → CSS, esbuild for JS, image optimization with Sharp)
2. **Python stage**: Runs Django/Wagtail with compiled assets baked in

Frontend assets are built into the image, not mounted as volumes in production.

### Database Switching
Database selection is controlled by the `DATABASE` environment variable in `.env`:
- `DATABASE=sqlite` (default) - No container needed
- `DATABASE=postgres` - PostgreSQL 16 with Adminer at localhost:8080
- `DATABASE=mysql` - MySQL 8 with Adminer at localhost:8080

The Makefile automatically loads the appropriate `compose.*.override.yaml` file. Settings in `app/settings/base.py` auto-detect database from environment variables. Run `make check-env` to validate configuration before building.

### Django Settings Structure
- `app/settings/base.py` - Core settings, auto-detects database
- `app/settings/dev.py` - Development overrides (DEBUG=True, browser reload, style guide)
- `app/settings/production.py` - Production settings

Default is dev mode. Set `DJANGO_SETTINGS_MODULE=app.settings.production` for production.

### Wagtail Page Architecture
All pages extend `wagtail.models.Page`. The HomePage model in `app/home/models.py` is the entry point. Wagtail's serving mechanism handles routing (catch-all pattern in urls.py). Pages are hierarchical in the Wagtail admin tree.

To add new page types:
1. Create model extending Page in an app's models.py
2. Add content_panels for admin fields
3. Create template in app/templates/{app}/{model_name_snake_case}.html
4. Run makemigrations and migrate

### Frontend Build Pipeline

**Source → Compiled:**
- `static_src/scss/` → `static_compiled/css/` (SASS compilation)
- `static_src/js/` → `static_compiled/js/` (esbuild bundling)
- `static_src/img/` → `static_compiled/img/` (Sharp optimization: max 1920x1080, JPEG 80%, WebP)

**Key Tools:**
- **Pico CSS** (v2.1): Classless/semantic CSS framework, configured in `static_src/scss/app.scss` with "pumpkin" theme
- **esbuild**: Fast JS bundler, single entry point at `static_src/js/app.js`
- **concurrently**: Runs multiple watch tasks in parallel

**Template Styling Pattern:**
Use `{% block extra_css %}` in templates for page-specific styles. See `app/home/templates/home/home_page.html` for reference. Global styles go in `static_src/scss/components/`.

### URL Routing Priority
1. `/django-admin/` - Django admin
2. `/admin/` - Wagtail admin
3. `/documents/` - Document serving
4. `/search/` - Search functionality
5. `/style-guide/` - Pico CSS demo (dev only)
6. `/` - Wagtail page serving (catch-all)

## Testing

Tests use Django's TestCase class. Located in `app/{app_name}/tests.py`. Run with `make test`.

Current test coverage: HomePage views (frontend, admin operations like edit/delete/copy).

## Code Quality

**Linting/Formatting:**
- Ruff (Black-compatible, configured in pyproject.toml)
- Pre-commit hooks: Ruff, pyupgrade (--py310-plus), django-upgrade (--target-version 5.2)
- Excludes: migrations, node_modules, static_compiled

**CI/CD (.github/workflows/ci.yml):**
Runs pre-commit checks and test suite on push to main and pull requests.

## Development Tools

**MailHog**: Email testing at http://localhost:8025 (captures SMTP in dev)

**Browser Reload**: `django-browser-reload` auto-refreshes on backend changes (dev only)

**Adminer**: Database UI at http://localhost:8080 (PostgreSQL/MySQL only)

**Sample Content**: `python manage.py create_sample_media` generates test images and documents

## Important Conventions

- Django apps in `app/` directory
- Templates follow `app/templates/{app}/{model_snake_case}.html`
- Static source in `static_src/`, compiled to `static_compiled/` (gitignored)
- Wagtail admin user required: `make superuser`
- Style guide (`app/style_guide/`) is removable for production
- Frontend changes require rebuild: `npm run build` then `make collectstatic` in Docker

## Common Workflows

**Add a new Wagtail page type:**
1. Create model in `app/{app}/models.py` extending Page
2. Add template at `app/{app}/templates/{app}/{model_snake}.html`
3. `make sh` then `python manage.py makemigrations && python manage.py migrate`
4. Add page via Wagtail admin

**Change databases:**
1. Update `DATABASE=postgres` in `.env`
2. `make down && make check-env && make build && make up && make migrate`

**Deploy frontend changes:**
1. Edit files in `static_src/`
2. `npm run build` (or `npm start` in watch mode)
3. In Docker: `make collectstatic` if needed for production

**Run single test:**
```bash
make sh
python manage.py test app.home.tests.HomePageTests.test_homepage_view
```

## Documentation Resources

**Official Wagtail Documentation**: https://docs.wagtail.org/en/stable/

Key sections for this project:
- **Getting Started**: https://docs.wagtail.org/en/stable/getting_started/index.html
- **Page Models**: https://docs.wagtail.org/en/stable/topics/pages.html
- **Snippets**: https://docs.wagtail.org/en/stable/topics/snippets.html
- **Images**: https://docs.wagtail.org/en/stable/topics/images.html
- **StreamField**: https://docs.wagtail.org/en/stable/topics/streamfield.html
- **Search**: https://docs.wagtail.org/en/stable/topics/search/index.html
- **Testing**: https://docs.wagtail.org/en/stable/advanced_topics/testing.html

**Django Documentation**: https://docs.djangoproject.com/en/5.2/

**Pico CSS Documentation**: https://picocss.com/docs
