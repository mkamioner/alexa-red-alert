from typing import Any, Optional
import os

import boto3


def create_local_dynamodb_client(local_port: Optional[int] = None) -> boto3.client:
    port = local_port or int(os.getenv("LOCAL_DYNAMODB_PORT", "8042"))
    return boto3.client(
        "dynamodb",
        endpoint_url=f"http://0.0.0.0:{port}",
        region_name="local",
        aws_access_key_id="local",
        aws_secret_access_key="local",
    )


def create_local_dynamodb_table(
    local_port: Optional[int] = None, table_name: str = "local-alexa-red-alert-data"
) -> Any:
    port = local_port or int(os.getenv("LOCAL_DYNAMODB_PORT", "8042"))
    resource = boto3.resource(
        "dynamodb", endpoint_url=f"http://0.0.0.0:{port}", region_name="local"
    )
    return resource.Table(table_name)


def reset_local_dynamodb(client: boto3.client) -> None:
    if client.meta.region_name != "local":
        raise RuntimeError("Cannot reset DynamoDB tables on non-local database")

    list_tables_response = client.list_tables()

    for table_name in list_tables_response["TableNames"]:
        client.delete_table(TableName=table_name)


def create_data_table(client: boto3.client) -> str:
    table_name = "local-alexa-red-alert-data"
    client.create_table(
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "pk1", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
            {"AttributeName": "sk1", "AttributeType": "S"},
        ],
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        BillingMode="PAY_PER_REQUEST",
        GlobalSecondaryIndexes=[
            {
                "IndexName": "pk1-sk1",
                "KeySchema": [
                    {"AttributeName": "pk1", "KeyType": "HASH"},
                    {"AttributeName": "sk1", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
    )

    return table_name
