from typing import Any, Optional
import json

import urllib3

from alexa_red_alert.alert import Alert, parse_alert
from alexa_red_alert.alert_category import AlertCategory, parse_alert_category
from alexa_red_alert.district import District, parse_district

HTTP_POOL = urllib3.PoolManager()


class AlertChecker:
    def __init__(self):
        self.metadata_loaded = False

        self._districts_by_hebrew_name: dict[str, District] = {}
        self._alert_categories_by_id: dict[str, AlertCategory] = {}

    def load_metadata(self) -> None:
        self._districts_by_hebrew_name = {
            district.hebrew_name: district for district in self._get_districts()
        }
        self._alert_categories_by_id = {
            str(alert_category.category_id): alert_category
            for alert_category in self._get_alert_categories()
        }

        self.metadata_loaded = True

    @classmethod
    def _get_districts(cls) -> list[District]:
        response = HTTP_POOL.request(
            method="GET",
            url="https://www.oref.org.il//Shared/Ajax/GetDistricts.aspx?lang=en",
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Host": "www.oref.org.il",
                "Referer": "https://www.oref.org.il/en",
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
                ),
            },
        )

        if response.status != 200:
            raise ValueError(f"Got status of {response.status}")

        return [parse_district(district) for district in cls._parse_body(response)]

    @classmethod
    def _get_alert_categories(cls) -> list[AlertCategory]:
        response = HTTP_POOL.request(
            method="GET",
            url="https://www.oref.org.il/Leftovers/en.Leftovers.json",
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Host": "www.oref.org.il",
                "Referer": "https://www.oref.org.il/en",
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
                ),
            },
        )

        if response.status != 200:
            raise ValueError(f"Got status of {response.status}")

        body = cls._parse_body(response)

        return [parse_alert_category(alert_category) for alert_category in body]

    @staticmethod
    def _parse_body(response: Any) -> Any:
        # https://stackoverflow.com/questions/17912307/u-ufeff-in-python-string
        try:
            return json.loads(response.data.decode("utf-8-sig"))
        except json.JSONDecodeError:
            return None

    def scan(self) -> Optional[Alert]:
        if not self.metadata_loaded:
            raise RuntimeError("Must load metadata before checking alerts")

        response = HTTP_POOL.request(
            method="GET",
            url="https://www.oref.org.il/WarningMessages/alert/alerts.json",
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Host": "www.oref.org.il",
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://www.oref.org.il/en",
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
                ),
            },
        )

        if response.status != 200:
            raise ValueError(f"Got status of {response.status}")

        if body := self._parse_body(response):
            return parse_alert(body)

        return None

    def get_districts(self, alert: Alert) -> list[District]:
        if not self.metadata_loaded:
            raise RuntimeError("Must load metadata before getting districts")

        return [
            self._districts_by_hebrew_name[location] for location in alert.locations
        ]

    def get_alert_category(self, alert: Alert) -> AlertCategory:
        if not self.metadata_loaded:
            raise RuntimeError("Must load metadata before getting alert category")

        return self._alert_categories_by_id[alert.alert_category_id]
