import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import init_db, get_db_status, get_db
from app.routers import (
    auth, dashboard, buildings, energy, water, traffic,
    facilities, analytics, alerts, datasets, ml, settings as settings_router
)

logger = logging.getLogger("smart_campus.api")
logging.basicConfig(level=logging.INFO)

import threading

def _background_init():
    try:
        logger.info("Initializing database connection in background...")
        db, status_str = init_db()
        if db is not None and status_str == "connected":
            try:
                user_count = db.users.count_documents({})
                if user_count == 0:
                    logger.info("Database empty on startup. Triggering auto-seeding...")
                    import sys, os
                    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
                    from database.seed_data import seed_database
                    from backend.ml.pipeline import run_ml_pipeline
                    seed_database(force=True)
                    run_ml_pipeline(source="simulated")
            except Exception as err:
                logger.warning(f"Startup background auto-seed notice: {err}")
    except Exception as err:
        logger.warning(f"Background database init notice: {err}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Smart Campus Digital Twin API Backend (Instant Port Binding Mode)...")
    init_thread = threading.Thread(target=_background_init, daemon=True)
    init_thread.start()
    yield
    logger.info("Shutting down Smart Campus Digital Twin API Backend...")

app = FastAPI(
    title="AI Digital Twin for Smart Campus",
    description="Predictive Intelligence API for Energy, Water, Traffic & Facility Management",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.3f}s")
    return response

from fastapi.exceptions import RequestValidationError

# Request Validation Error Handler (returns field-specific details)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field_name = " -> ".join([str(loc) for loc in err.get("loc", []) if loc != "body"])
        msg = err.get("msg", "invalid")
        if field_name:
            errors.append(f"Form Field '{field_name}': {msg}")
        else:
            errors.append(msg)
    detail_msg = "; ".join(errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": f"Request Error: {detail_msg}"}
    )

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."}
    )

# Health endpoint
@app.get("/api/health")
def health_check():
    db_status = get_db_status()
    return {
        "status": "ok",
        "database": db_status,
        "service": "Smart Campus AI Digital Twin Engine"
    }

# Include Routers under /api
api_prefix = "/api"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(buildings.router, prefix=api_prefix)
app.include_router(energy.router, prefix=api_prefix)
app.include_router(water.router, prefix=api_prefix)
app.include_router(traffic.router, prefix=api_prefix)
app.include_router(facilities.router, prefix=api_prefix)
app.include_router(analytics.router, prefix=api_prefix)
app.include_router(alerts.router, prefix=api_prefix)
app.include_router(datasets.router, prefix=api_prefix)
app.include_router(ml.router, prefix=api_prefix)
app.include_router(settings_router.router, prefix=api_prefix)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
