import requests
from helpers import get_file_metadata, upload_object_to_s3, get_link_stub
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_one_handler(event, context):
    logger.info(f"function started by {event}")
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
        for item in metadata:
            logger.info(f"Processing {item}, {type(item)=}")
            link_stub = get_link_stub(item["link"])
            key = item["file_name"]
            object_content = requests.get(
                f"{base_url}{link_stub}", timeout=5, headers=headers
            )
            bucket_name = os.environ["BUCKET_NAME"]
            upload_object_to_s3(
                bucket_name=bucket_name,
                key=key,
                object_content=object_content.content,
                metadata=item,
            )
    except Exception as e:
        logger.error(f"Unable to load object to bucket - {e}", exc_info=True)

    return {"status_code": 200, "body": "Successfully loaded data"}
