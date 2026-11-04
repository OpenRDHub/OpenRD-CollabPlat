"""Task lifecycle rules shared by status changes and historical data repair."""

TEAM_STATUS_BY_TASK_STATUS = {
    "recruiting": "forming",
    "team_ready": "collaborating",
    "in_progress": "collaborating",
    "pending_acceptance": "collaborating",
    "completed": "accepted",
    "closed": "ended",
}


def apply_task_status(task, status: str) -> None:
    team_status = TEAM_STATUS_BY_TASK_STATUS[status]
    task.status = status
    task.team_status = team_status
