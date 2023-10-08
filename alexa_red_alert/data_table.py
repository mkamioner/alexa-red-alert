from dataclasses import asdict
from time import time
from typing import Any, Generator, Optional

from boto3.dynamodb.conditions import Attr, Key
import boto3

from alexa_red_alert.alert import Alert
from alexa_red_alert.alert_category import AlertCategory
from alexa_red_alert.district import District

DYNAMODB_CLIENT = boto3.client("dynamodb", region_name="il-central-1")


class DataTable:
    def __init__(self, table: Any, re_alert_at_s: int = 120):
        self._table = table
        self._re_alert_at_s = re_alert_at_s

    @staticmethod
    def create_from_table_name(
        table_name: str = "alexa-red-alert-data-table",
        dynamodb_resource: Optional[Any] = None,
        re_alert_at_s: int = 120,
    ) -> "DataTable":
        dynamodb = dynamodb_resource or boto3.resource(
            "dynamodb", region_name="il-central-1"
        )
        table = dynamodb.Table(table_name)

        return DataTable(table, re_alert_at_s)

    def upsert_alert(
        self, alert: Alert, districts: list[District], alert_category: AlertCategory
    ) -> None:
        now_s = int(time())
        ttl_s = now_s + (alert_category.duration_minutes * 60)
        re_alert_at_s = now_s + self._re_alert_at_s

        for district in districts:
            update_values = {
                "expires_at_s": ttl_s,
                "re_alert_at_s": re_alert_at_s,
                "created_at_s": now_s,
                "alert": asdict(alert),
                "district": asdict(district),
                "alert_category": asdict(alert_category),
                "pk1": f"DISTRICT#{district.district_id}",
                "sk1": f"CATEGORY#{alert_category.code_name}",
            }
            try:
                self._table.update_item(
                    Key={
                        "pk": f"AREA#{district.area_id}",
                        "sk": "#".join(
                            [
                                "DISTRICT",
                                district.district_id,
                                "CATEGORY",
                                alert_category.code_name,
                            ]
                        ),
                    },
                    UpdateExpression=(
                        f"SET {', '.join(f'#{field} = :{field}' for field in update_values)}"
                    ),
                    ExpressionAttributeNames={
                        f"#{field}": f"{field}" for field in update_values
                    },
                    ExpressionAttributeValues={
                        f":{key}": value for key, value in update_values.items()
                    },
                    ConditionExpression=(
                        Attr("pk").not_exists() | Attr("re_alert_at_s").lte(now_s)
                    ),
                )
            except DYNAMODB_CLIENT.exceptions.ConditionalCheckFailedException:
                pass

    def get_status_by_area(self, area_id: str) -> Generator[None, None, dict[str, Any]]:
        now_s = int(time())
        query_kwargs = {
            "ConsistentRead": True,
            "KeyConditionExpression": Key("pk").eq(f"AREA#{area_id}"),
            "FilterExpression": Attr("expires_at_s").gte(now_s),
        }

        while True:
            result = self._table.query(**query_kwargs)

            yield from result["Items"]

            if last_evaluated_key := result.get("LastEvaluatedKey"):
                query_kwargs["ExclusiveStartKey"] = last_evaluated_key
            else:
                break

    def get_status_by_district_ids(
        self, district_ids: list[str]
    ) -> Generator[None, None, dict[str, Any]]:
        now_s = int(time())
        for district_id in district_ids:
            query_kwargs = {
                "IndexName": "pk1-sk1",
                "KeyConditionExpression": Key("pk1").eq(f"DISTRICT#{district_id}"),
                "FilterExpression": Attr("expires_at_s").gte(now_s),
            }

            while True:
                result = self._table.query(**query_kwargs)

                yield from result["Items"]

                if last_evaluated_key := result.get("LastEvaluatedKey"):
                    query_kwargs["ExclusiveStartKey"] = last_evaluated_key
                else:
                    break

    def get_status_all(self) -> Generator[None, None, dict[str, Any]]:
        now_s = int(time())
        scan_kwargs = {
            "ConsistentRead": True,
            "FilterExpression": Attr("expires_at_s").gte(now_s),
        }

        while True:
            result = self._table.scan(**scan_kwargs)

            yield from result["Items"]

            if last_evaluated_key := result.get("LastEvaluatedKey"):
                scan_kwargs["ExclusiveStartKey"] = last_evaluated_key
            else:
                break
