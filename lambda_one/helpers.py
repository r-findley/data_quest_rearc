import hashlib
import logging
import re
from datetime import datetime

import boto3

from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_datetime_from_metadata(text_parts: list) -> str | None:
    """
    Extracts and parses a datetime string from a list of metadata parts.

    Args:
        text_parts (list): List containing date and time strings.

    Returns:
        str | None: ISO formatted datetime string, or None if parsing fails.

    Example:
        >>> get_datetime_from_metadata(["11/17/2011", "5:11 PM", "SomeText"])
        '2011-11-17T17:11:00'
    """
    try:
        dt_str = f"{text_parts[0]} {text_parts[1]} {text_parts[2]}"
        last_modified = datetime.strptime(dt_str, "%m/%d/%Y %I:%M %p")
        return last_modified.isoformat()
    except TypeError:
        logger.error(f"The {text_parts} passed was not a list.")


def get_file_size_from_metadata(text_parts: list) -> str | None:
    """
    Extracts the file size from a list of metadata parts.

    Args:
        text_parts (list): List containing file size as the fourth element.

    Returns:
        str | None: File size as a string, or None if parsing fails.

    Example:
        >>> get_file_size_from_metadata(["date", "time", "other", "12345"])
        '12345'
    """
    try:
        file_size = text_parts[3]
        return file_size
    except TypeError:
        logger.error(f"The {text_parts} passed was not a list.")


def get_link_from_metadata(text_parts: list) -> object:
    """
    Extracts and parses the HTML anchor tag from metadata parts.

    Args:
        text_parts (list): List containing HTML anchor tag parts.

    Returns:
        object: BeautifulSoup object representing the anchor tag, or None if parsing fails.

    Example:
        >>> get_link_from_metadata(["irrelevant", "<a href='/file.txt'>file.txt</a>"])
        <a href="/file.txt">file.txt</a>
    """
    try:
        anchor_html = " ".join(text_parts[4:])
        link = BeautifulSoup(anchor_html, "html.parser")
        return link
    except TypeError:
        logger.error(f"The {text_parts} passed was not a list.")


def get_file_name_from_metadata(text_parts: list) -> str | None:
    """
    Extracts the file name from the HTML anchor tag in metadata parts.

    Args:
        text_parts (list): List containing HTML anchor tag parts.

    Returns:
        str | None: File name as a string, or None if parsing fails.

    Example:
        >>> get_file_name_from_metadata(["irrelevant", "<a href='/file.txt'>file.txt</a>"])
        'file.txt'
    """
    try:
        link = get_link_from_metadata(text_parts)
        file_name = link.get_text(strip=True)
        return file_name
    except TypeError:
        logger.error(f"The {text_parts} passed was not a list.")


def get_hashsum(input_text: str) -> str | None:
    """
    Returns the MD5 hash of the input string.

    Args:
        input_text (str): The input string to hash.

    Returns:
        str | None: The MD5 hash as a hexadecimal string, or None if input is invalid.

    Example:
        >>> get_hashsum('hello')
        '5d41402abc4b2a76b9719d911017c592'
    """
    try:
        res = hashlib.md5(input_text.encode())
        return res.hexdigest()
    except TypeError:
        logger.error(f"The {input_text} passed was not a string.")


# TODO consider adding hashsum to metadata
def get_file_metadata(input_text: str):
    """
    Parses HTML text and extracts file metadata for each file listed.

    Args:
        input_text (str): HTML text containing file metadata.

    Returns:
        list: List of dictionaries with file metadata (file_name, link, file_size, source_last_modified).

    Example:
        >>> get_file_metadata('<a href="/file.txt">file.txt</a> 11/17/2011 5:11 PM 18343')
        [{'file_name': 'file.txt', 'link': '/file.txt', 'file_size': '18343', 'source_last_modified': '2011-11-17T17:11:00'}]
    """
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
    """Gets the href link from an anchor tag string. Returns None if not found.

    Args:
        text (str): HTML anchor tag string.

    Returns:
        str | None: The href link as a string, or None if not found.

    Example:
        >>> get_link_stub('<a href="/file.txt">file.txt</a>')
        '/file.txt'
    """
    try:
        match = re.search(r'href="([^"]+)"', text)
        if match:
            link_stub = match.group(1)
            return link_stub
        else:
            return None
    except Exception as e:
        logger.error(f"Unable to get link stub - {e}", exc_info=True)


def upload_object_to_s3(bucket_name: str, key: str, object_content, metadata):
    """
    Uploads an object to an S3 bucket with metadata.

    Args:
        bucket_name (str): Name of the S3 bucket.
        key (str): S3 object key.
        object_content (bytes): Content to upload.
        metadata (dict): Metadata to attach to the object.

    Returns:
        None

    Example:
        >>> upload_object_to_s3('my-bucket', 'file.txt', b'data', {'file_name': 'file.txt'})
    """
    try:
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=object_content,
            Metadata=metadata,
        )
    except Exception as e:
        logger.error(f"Failed to upload object to S3: {str(e)}")
        raise


def list_s3_objects_with_metadata(bucket_name: str, prefix: str = "") -> list[dict]:
    """
    Lists all objects in an S3 bucket along with their metadata.

    Args:
        bucket_name (str): Name of the S3 bucket.

    Returns:
        list: List of dictionaries with S3 object info and metadata.

    Example:
        >>> list_s3_objects_with_metadata('my-bucket')
        [{'Key': 'file.txt', 'LastModified': ..., 'Size': 123, 'Metadata': {...}}]
    """
    try:
        s3_client = boto3.client("s3")
        paginator = s3_client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

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


def sync_s3_with_bls_metadata(
    s3_client, bucket_name, bls_metadata, s3_objects
) -> list[str]:
    """
    Synchronizes S3 bucket contents with BLS.gov metadata.
    Deletes objects not present in BLS.gov, and returns a list of files that need upload (new or updated).
    Uses 'bls_data/{file_name}' as the S3 key for all BLS.gov files.

    Args:
        s3_client (boto3.client): Boto3 S3 client.
        bucket_name (str): Name of the S3 bucket.
        bls_metadata (list): List of BLS.gov metadata dicts.
        s3_objects (list): List of S3 object dicts.

    Returns:
        list: List of S3 keys that need to be uploaded to S3.

    Example:
        >>> sync_s3_with_bls_metadata(s3_client, 'my-bucket', bls_metadata, s3_objects)
        ['bls_data/file1.txt', 'bls_data/file2.txt']
    """
    files_to_upload = []
    try:
        bls_files = {f"bls_data/{item['file_name']}": item for item in bls_metadata}
        s3_files = {
            obj["Key"]: {
                "file_size": int(obj["Metadata"].get("file_size", obj["Size"])),
                "source_last_modified": obj["Metadata"].get("source_last_modified"),
            }
            for obj in s3_objects
        }
    except Exception as e:
        logger.error(f"Error processing metadata: {e}", exc_info=True)
        return []

    for s3_file in s3_files:
        if s3_file not in bls_files:
            logger.info(f"Deleting {s3_file} from S3 (not found in BLS metadata)")
            s3_client.delete_object(Bucket=bucket_name, Key=s3_file)

    for bls_key, bls_info in bls_files.items():
        s3_info = s3_files.get(bls_key)
        bls_size = int(bls_info["file_size"])
        bls_modified = str(bls_info.get("source_last_modified"))
        if s3_info:
            s3_size = s3_info["file_size"]
            s3_modified = str(s3_info.get("source_last_modified"))
            logger.info(
                f"Comparing for {bls_key}: BLS size={bls_size}, S3 size={s3_size}, BLS modified={bls_modified}, S3 modified={s3_modified}"
            )
            if bls_size != s3_size or bls_modified != s3_modified:
                logger.info(
                    f"Marking {bls_key} for upload (size or last_modified changed)"
                )
                s3_client.delete_object(Bucket=bucket_name, Key=bls_key)
                files_to_upload.append(bls_key)
        else:
            logger.info(f"Marking new file {bls_key} for upload to S3")
            files_to_upload.append(bls_key)
    return files_to_upload


def write_message_to_sqs(queue_url: str, message_body: str) -> None:
    """
    Sends a message to an SQS queue.

    Args:
        queue_url (str): URL of the SQS queue.
        message_body (str): The message body to send.

    Returns:
        None

    Example:
        >>> write_message_to_sqs('https://sqs.us-east-1.amazonaws.com/123456789012/my-queue', 'Hello, World!')
    """
    try:
        sqs_client = boto3.client("sqs")
        resp = sqs_client.send_message(QueueUrl=queue_url, MessageBody=message_body)
        logger.info(f"Message sent to SQS with MessageId: {resp.get('MessageId')}")
        return resp.get("MessageId")
    except Exception as e:
        logger.error(f"Failed to send message to SQS: {str(e)}")
        raise
