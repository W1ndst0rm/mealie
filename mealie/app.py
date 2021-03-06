import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# import utils.startup as startup
from app_config import APP_VERSION, PORT, PRODUCTION, WEB_PATH, docs_url, redoc_url
from routes import (
    backup_routes,
    debug_routes,
    meal_routes,
    migration_routes,
    setting_routes,
    static_routes,
    theme_routes,
    user_routes,
)
from routes.recipe import (
    all_recipe_routes,
    category_routes,
    recipe_crud_routes,
    tag_routes,
)
from utils.logger import logger

"""
TODO:
- [x] Fix Duplicate Category
- [x] Fix category overflow
- [ ] Enable Database Name Versioning
- [ ] Finish Frontend Category Management
    - [x] Delete Category
    - [ ] Sort Sidebar A-Z
- [ ] Refactor Test Endpoints - Abstract to fixture?


"""
app = FastAPI(
    title="Mealie",
    description="A place for all your recipes",
    version=APP_VERSION,
    docs_url=docs_url,
    redoc_url=redoc_url,
)


def mount_static_files():
    app.mount("/static", StaticFiles(directory=WEB_PATH, html=True))


def start_scheduler():
    import services.scheduler.scheduled_jobs


def api_routers():
    # Recipes
    app.include_router(all_recipe_routes.router)
    app.include_router(category_routes.router)
    app.include_router(tag_routes.router)
    app.include_router(recipe_crud_routes.router)
    # Meal Routes
    app.include_router(meal_routes.router)
    # Settings Routes
    app.include_router(setting_routes.router)
    app.include_router(theme_routes.router)
    # Backups/Imports Routes
    app.include_router(backup_routes.router)
    # User Routes
    app.include_router(user_routes.router)
    # Migration Routes
    app.include_router(migration_routes.router)
    app.include_router(debug_routes.router)


if PRODUCTION:
    mount_static_files()

api_routers()

# API 404 Catch all CALL AFTER ROUTERS
@app.get("/api/{full_path:path}", status_code=404, include_in_schema=False)
def invalid_api():
    return None


app.include_router(static_routes.router)


# Generate API Documentation
# if not PRODUCTION:
#     generate_api_docs(app)

start_scheduler()

if __name__ == "__main__":
    logger.info("-----SYSTEM STARTUP-----")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        debug=True,
        workers=1,
        forwarded_allow_ips="*",
    )
