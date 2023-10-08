from typing import Any
import json
import os

from boto3.dynamodb.transform import TypeDeserializer
import boto3

RED_ALERT_TOPIC_ARN = os.environ["RED_ALERT_TOPIC_ARN"]
DYNAMODB_TYPE_DESERIALIZER = TypeDeserializer()
RED_ALERT_TOPIC = boto3.resource("sns").Topic(RED_ALERT_TOPIC_ARN)


def process_record(record: dict[str, Any]) -> None:
    new_image = DYNAMODB_TYPE_DESERIALIZER.deserialize(record["dynamodb"]["NewImage"])
    message = {
        "createdAtS": int(new_image["created_at_s"]),
        "area": new_image["district"]["area_name"],
        "district": new_image["district"]["english_name"],
        "areaId": new_image["district"]["area_id"],
        "districtId": new_image["district"]["district_id"],
        "alert": new_image["alert_category"]["label"],
        "description": new_image["alert_category"]["description"],
        "alertId": new_image["alert"]["alert_id"],
    }
    print(json.dumps(message))
    RED_ALERT_TOPIC.publish(Message=json.dumps(message))


def lambda_handler(event: dict[str, Any], _: Any) -> None:
    print(json.dumps(event))

    for record in event["Records"]:
        process_record(record)

    print("Completed")
