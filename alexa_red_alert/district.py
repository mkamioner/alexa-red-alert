from dataclasses import dataclass
from typing import Any


@dataclass
class District:
    english_name: str
    code: str
    district_id: str
    area_id: str
    area_name: str
    hebrew_name: str
    migun_time_s: int


def parse_district(raw: dict[str, Any]) -> District:
    return District(
        english_name=raw["label"],
        code=raw["value"],
        district_id=raw["id"],
        area_id=str(raw["areaid"]),
        area_name=raw["areaname"],
        hebrew_name=raw["label_he"],
        migun_time_s=raw["migun_time"],
    )
