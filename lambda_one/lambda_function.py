import requests
from helpers import (
    get_file_metadata,
    upload_object_to_s3,
    get_link_stub,
    list_s3_objects_with_metadata,
    sync_s3_with_bls_metadata,
)
import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_one_handler(event, context):
    logger.info(f"function started by {event}")
    bucket_name = os.environ["BUCKET_NAME"]
    s3_client = boto3.client("s3")
    objects_in_bucket = []
    metadata = []
    try:
        objects_in_bucket = list_s3_objects_with_metadata(bucket_name=bucket_name)
    except Exception as e:
        logger.error(f"Unable to list objects in bucket - {e}", exc_info=True)

    try:
        headers = {
            "user-agent": "My interview prep, contact me at ryanfindley1013@gmail.com"
        }
        base_url = "https://download.bls.gov/"
        response = requests.get(
            f"{base_url}/pub/time.series/pr/", timeout=5, headers=headers
        )
        if response.status_code == 200:
            metadata = get_file_metadata(response.text)
    except Exception as e:
        logger.error(f"Unable to retrieve and process data - {e}", exc_info=True)

    try:
        sync_s3_with_bls_metadata(
            s3_client=s3_client,
            bucket_name=bucket_name,
            bls_metadata=metadata,
            s3_objects=objects_in_bucket,
        )
    except Exception as e:
        logger.error(f"Unable to sync S3 with BLS metadata - {e}", exc_info=True)

    try:
        for item in metadata:
            key = item["file_name"]
            s3_obj = next((obj for obj in objects_in_bucket if obj["Key"] == key), None)
            needs_upload = (
                s3_obj is None
                or item["file_size"] != s3_obj["Size"]
                or item.get("source_last_modified")
                != s3_obj.get("source_last_modified")
            )
            if needs_upload:
                link_stub = get_link_stub(item["link"])
                object_content = requests.get(
                    f"{base_url}{link_stub}", timeout=5, headers=headers
                )
                upload_object_to_s3(
                    bucket_name=bucket_name,
                    key=key,
                    object_content=object_content.content,
                    metadata=item,
                )
    except Exception as e:
        logger.error(f"Unable to load object to bucket - {e}", exc_info=True)

    return {"status_code": 200, "body": "Successfully loaded data"}
