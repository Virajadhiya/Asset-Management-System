from fastapi import APIRouter
from app.api import auth, bridges, inspections, maintenance, lifecycle, dashboard, gis, audit, issues

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(bridges.router, prefix="/bridges", tags=["bridges"])
api_router.include_router(inspections.router, tags=["inspections"])
api_router.include_router(maintenance.router, tags=["maintenance"])
api_router.include_router(lifecycle.router, tags=["lifecycle"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(gis.router, prefix="/gis", tags=["gis"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(issues.router, prefix="/issues", tags=["issues"])
