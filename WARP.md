# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Type

Django backend application (Python)

## Common Commands

### Development Server
```bash
python manage.py runserver
```

### Database Migrations
```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test <app_name>

# Run specific test
python manage.py test <app_name>.tests.<TestClass>.<test_method>
```

### Django Shell
```bash
# Access Django shell for debugging/testing
python manage.py shell
```

### Static Files
```bash
# Collect static files for production
python manage.py collectstatic --noinput
```

### Create Superuser
```bash
python manage.py createsuperuser
```

## Project Setup

This is a new Django project. When code is added, typical structure will include:
- Django apps organized by feature/domain
- Models in `models.py` within each app
- Views/ViewSets for API endpoints
- URL routing in `urls.py` files
- Settings split between base, development, and production configurations
- Environment variables managed via `.env` file (not tracked in git)

## Architecture Notes

- Django backend, likely REST API using Django REST Framework
- Database migrations managed via Django ORM
- Static files collected to `staticfiles/` directory
- Media uploads stored in `media/` directory
- SQLite for development, likely PostgreSQL for production
