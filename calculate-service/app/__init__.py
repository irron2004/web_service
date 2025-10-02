from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .instrumentation import RequestContextMiddleware
from .routers import health, pages, problems


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        docs_url="/docs" if settings.enable_openapi else None,
        redoc_url=None,
    )

    # Ensure templates/tests can resolve relative paths when run from any CWD.
    base_dir = Path(__file__).resolve().parent
    static_dir = base_dir / "static"
    template_dir = base_dir / "templates"

    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    templates = Jinja2Templates(directory=template_dir)

    app.add_middleware(RequestContextMiddleware)

    # Store frequently used resources on the application state so ancillary
    # components (health checks, background tasks, etc.) can reuse them without
    # rebuilding instances.
    app.state.settings = settings
    app.state.templates = templates

    app.include_router(health.router)
    app.include_router(pages.get_router(templates))
    app.include_router(problems.router)

    return app


app = create_app()


__all__ = ["create_app", "app"]
