from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    total_transactions: int = 0
    total_datasets: int = 0
    flagged_accounts: int = 0
    active_cases: int = 0
    risk_distribution: dict = {}
    latest_alerts: list[dict] = []
