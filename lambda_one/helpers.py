from datetime import datetime
from bs4 import BeautifulSoup
import hashlib
import logging
import boto3
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_datetime_from_metadata(text_parts: list) -> str | None:
    try:
        dt_str = f"{text_parts[0]} {text_parts[1]} {text_parts[2]}"
        last_modified = datetime.strptime(dt_str, "%m/%d/%Y %I:%M %p")
        return last_modified.isoformat()
    except TypeError:
        logger.error(f"The {text_parts} passed was not a list.")


def get_file_size_from_metadata(text_parts: list) -> str | None:
    try:
        file_size = text_parts[3]
        return file_size
    except TypeError:
        logger.error(f"The {text_parts} passed was not a list.")


def get_link_from_metadata(text_parts: list) -> object:
    try:
        anchor_html = " ".join(text_parts[4:])
        link = BeautifulSoup(anchor_html, "html.parser")
        return link
    except TypeError:
        logger.error(f"The {text_parts} passed was not a list.")


def get_file_name_from_metadata(text_parts: list) -> str | None:
    try:
        link = get_link_from_metadata(text_parts)
        file_name = link.get_text(strip=True)
        return file_name
    except TypeError:
        logger.error(f"The {text_parts} passed was not a list.")


# TODO Consider adding to metadata for further validation
def get_hashsum(input_text: str) -> str | None:
    try:
        res = hashlib.md5(input_text.encode())
        return res.hexdigest()
    except TypeError:
        logger.error(f"The {input_text} passed was not a string.")


def get_file_metadata(input_text: str):
    cleaned_text = input_text.replace("<br>", ",")
    lines = cleaned_text.split(",")
    cleaned_lines = [
        line.strip()
        for line in lines
        if "HREF" in line and "[To Parent Directory]" not in line
    ]
    file_info = []
    for line in cleaned_lines:
        parts = line.strip().split()
        file_info.append(
            {
                "file_name": get_file_name_from_metadata(parts),
                "link": str(get_link_from_metadata(parts)),
                "file_size": get_file_size_from_metadata(parts),
                "source_last_modified": get_datetime_from_metadata(parts),
            }
        )
    return file_info


def get_link_stub(text: str) -> str | None:
    try:
        match = re.search(r'href="([^"]+)"', text)
        link_stub = match.group(1)
        return link_stub
    except Exception as e:
        logger.error(f"Unable to get link stub - {e}", exc_info=True)


def upload_object_to_s3(bucket_name, key, object_content, metadata):
    try:
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Bucket=bucket_name, Key=key, Body=object_content, Metadata=metadata
        )
    except Exception as e:
        logger.error(f"Failed to upload object to S3: {str(e)}")
        raise


def list_s3_objects_with_metadata(bucket_name):
    try:
        s3_client = boto3.client("s3")
        paginator = s3_client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(Bucket=bucket_name)

        objects_with_metadata = []
        for page in page_iterator:
            if "Contents" in page:
                for obj in page["Contents"]:
                    head_response = s3_client.head_object(
                        Bucket=bucket_name, Key=obj["Key"]
                    )
                    metadata = head_response.get("Metadata", {})
                    objects_with_metadata.append(
                        {
                            "Key": obj["Key"],
                            "LastModified": obj["LastModified"],
                            "Size": obj["Size"],
                            "Metadata": metadata,
                        }
                    )
        return objects_with_metadata
    except Exception as e:
        logger.error(f"Failed to list objects with metadata from S3: {str(e)}")
        raise


def sync_s3_with_bls_metadata(s3_client, bucket_name, bls_metadata, s3_objects):
    try:
        bls_files = {item["file_name"]: item for item in bls_metadata}
        s3_files = {
            obj["Key"]: {
                "file_size": int(obj["Size"]),
                "source_last_modified": obj["Metadata"].get("source_last_modified"),
            }
            for obj in s3_objects
        }
    except Exception as e:
        logger.error(f"Error processing metadata: {e}", exc_info=True)
        return

    for s3_file in s3_files:
        if s3_file not in bls_files:
            logger.info(f"Deleting {s3_file} from S3 (not found in BLS metadata)")
            s3_client.delete_object(Bucket=bucket_name, Key=s3_file)

    for bls_file, bls_info in bls_files.items():
        s3_info = s3_files.get(bls_file)
        if s3_info:
            if int(bls_info["file_size"]) != s3_info["file_size"] or bls_info.get(
                "source_last_modified"
            ) != s3_info.get("source_last_modified"):
                logger.info(
                    f"Updating {bls_file} in S3 (size or last_modified changed)"
                )
                s3_client.delete_object(Bucket=bucket_name, Key=bls_file)

        else:
            logger.info(f"Uploading new file {bls_file} to S3")
