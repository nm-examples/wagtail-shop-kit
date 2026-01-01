# Installation Guide

This guide will help you set up the Wagtail Shop Kit development environment on your local machine.

## Requirements

### Required

- [Python >= 3.10](https://www.python.org/downloads/) (development and deployment)
- [Docker](https://www.docker.com/) (for local development)
- [Docker Compose](https://docs.docker.com/compose/) (for local development)
- [Node.js](https://nodejs.org/en/) (for frontend build tools in development)

### Optional

- [Git](https://git-scm.com/) (optional, for version control)
- [Make](https://www.gnu.org/software/make/) (optional, for running commands)
- [NVM](https://github.com/nvm-sh/nvm) (optional, for managing Node versions)
- [pre-commit](https://pre-commit.com/) (optional, for running code checks)
- [UV](https://github.com/astral-sh/uv) (optional, for managing Python dependencies)

## Getting Started

Follow these steps to set up the project:

1. Clone this repository to a location on your computer
2. Change into the project directory
3. Copy `.env.example` to `.env` and choose your database (default is SQLite). Set `DATABASE=sqlite|postgres|mysql`.
4. Run `make build` to build the Docker containers
5. Run `make up` to start the Docker containers
6. Run `make migrate` to apply database migrations
7. Run `make superuser` to create a superuser
8. Run `make run` to start the Django development server

**Note:** `.env` is required. `make build` and `make up` validate environment variables via `make check-env` and will fail if required values are missing. See `.env.example` for all keys.

## Quick Start

There is a make command to run most of the steps above in one go:

```bash
make quickstart
```

You'll need to run `make superuser` separately to create your admin user.

## Default Configuration

If you haven't changed `.env` the app will default to:

- Use SQLite as the database
- A mail utility will be available at [http://localhost:8025](http://localhost:8025)
- A database management utility will be available at [http://localhost:8080](http://localhost:8080)

## Accessing the Site

Once the development server is running:

- **Main site**: [http://localhost:8000](http://localhost:8000)
- **Wagtail admin**: [http://localhost:8000/admin](http://localhost:8000/admin)
- **Style guide**: [http://localhost:8000/style-guide](http://localhost:8000/style-guide) (only available in debug mode)

## Next Steps

- See [Backend Development](./backend-development.md) for information about database configuration and backend development
- See [Frontend Development](./frontend-development.md) for information about building CSS and JavaScript assets
- See [Management Commands](./management-commands.md) for helpful commands to generate sample content and manage data
