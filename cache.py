import boto3
import time
import json
import os
from boto3.dynamodb.conditions import Key

TABLE_NAME = "valorant-match-cache"
TTL_SECONDS = 60 * 60 * 24  # 24 hours

dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
table = dynamodb.Table(TABLE_NAME)


def _make_ttl() -> int:
    return int(time.time()) + TTL_SECONDS


def cache_matches(puuid: str, matches: list[dict]) -> None:
    with table.batch_writer() as batch:
        for match in matches:
            match_id = match.get("match_id")
            if not match_id:
                continue
            batch.put_item(Item={
                "puuid":    puuid,
                "match_id": match_id,
                "data":     json.dumps(match),
                "ttl":      _make_ttl(),
            })


def get_cached_matches(puuid: str) -> list[dict]:
    response = table.query(
        KeyConditionExpression=Key("puuid").eq(puuid),
        FilterExpression="#ttl > :now",
        ExpressionAttributeNames={
            "#ttl": "ttl"
        },
        ExpressionAttributeValues={
            ":now": int(time.time())
        },
    )
    return [json.loads(item["data"]) for item in response.get("Items", [])]


def is_match_cached(puuid: str, match_id: str) -> bool:
    response = table.get_item(Key={"puuid": puuid, "match_id": match_id})
    item = response.get("Item")
    if not item:
        return False
    return item.get("ttl", 0) > int(time.time())