from typing import Any
import decimal
import json
import os

from alexa_red_alert.data_table import DataTable

DATA_TABLE = DataTable.create_from_table_name(os.environ["DATA_TABLE_NAME"])


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)

        return super().default(o)


def lambda_handler(event: dict[str, Any], _: Any) -> dict[str, Any]:
    print(event)
    multi_value_query_string_params = event.get("multiValueQueryStringParameters") or {}
    print(f"{multi_value_query_string_params=}")

    alerts = []

    if area_ids := multi_value_query_string_params.get("a"):
        for area_id in area_ids:
            alerts.extend(DATA_TABLE.get_status_by_area(area_id))
    elif district_ids := multi_value_query_string_params.get("d"):
        for district_id in district_ids:
            alerts.extend(DATA_TABLE.get_status_by_district_ids(district_id))
    else:
        alerts.extend(DATA_TABLE.get_status_all())

    payload = {"alerts": alerts, "exists": bool(alerts), "full": True}

    if multi_value_query_string_params.get("full", [0])[0] != "1":
        payload["full"] = False
        payload["alerts"] = [
            {
                "category": alert["alert_category"]["label"],
                "area": alert["district"]["area_name"],
                "area_id": alert["district"]["area_id"],
                "district_id": alert["district"]["district_id"],
                "migun_time_s": alert["district"]["migun_time_s"],
                "created_at_s": alert["created_at_s"],
                "description": alert["alert_category"]["description"],
            }
            for alert in alerts
        ]

    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(payload, cls=DecimalEncoder),
    }
