from fastapi import APIRouter

from app.api.v1.accounts import router as accounts_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.auth import router as auth_router
from app.api.v1.cases import router as cases_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.datasets import router as datasets_router
from app.api.v1.demo import router as demo_router
from app.api.v1.graph import router as graph_router
from app.api.v1.analysis_runs import router as analysis_runs_router
from app.api.v1.health import router as health_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(datasets_router)
api_router.include_router(alerts_router)
api_router.include_router(accounts_router)
api_router.include_router(graph_router)
api_router.include_router(cases_router)
api_router.include_router(demo_router)
api_router.include_router(dashboard_router)
api_router.include_router(analysis_runs_router)
api_router.include_router(health_router)
