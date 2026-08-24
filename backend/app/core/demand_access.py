from typing import Protocol


class DemandAccessSubject(Protocol):
    creator_id: str
    owner_id: str | None


def can_access_demand_private_content(
    demand: DemandAccessSubject,
    current_user: dict,
) -> bool:
    """Return whether a user may read a demand's private business content."""
    user_id = current_user["user_id"]
    role = current_user["role"]
    return (
        demand.creator_id == user_id
        or demand.owner_id == user_id
        or role in ("operator", "super_admin")
    )
