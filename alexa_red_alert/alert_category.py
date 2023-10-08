from dataclasses import dataclass
from typing import Any


@dataclass
class AlertCategory:
    category_id: int
    code_name: str
    duration_minutes: int
    label: str
    description: str


def parse_alert_category(raw: dict[str, Any]) -> AlertCategory:
    return AlertCategory(
        category_id=raw["category"],
        code_name=raw["code"],
        duration_minutes=raw["duration"],
        label=raw["label"],
        description=raw["description1"],
    )
