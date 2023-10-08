from dataclasses import dataclass
from typing import Any


@dataclass
class Alert:
    alert_id: str
    alert_category_id: str
    title: str
    locations: list[str]
    description: str


def parse_alert(raw: dict[str, Any]) -> Alert:
    # locations = chain.from_iterable([line.split(", ") for line in raw["data"]])
    return Alert(
        alert_id=raw["id"],
        alert_category_id=raw["cat"],
        title=raw["title"],
        locations=raw["data"],
        description=raw["desc"],
    )
