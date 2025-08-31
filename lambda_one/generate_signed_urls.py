import boto3
from datetime import datetime
import logging
from urllib.parse import quote


def generate_signed_url(client, bucket: str, key: str, expires_in=86400):
    return client.generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expires_in
    )


def generate_index_html(objects: list, prefix: str):
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

        html = f"""<!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <title>Listing for {prefix}</title>
            <style>
            body {{ font-family: system-ui, sans-serif; padding: 24px; }}
            h1 {{ font-size: 20px; margin-bottom: 12px; }}
            table {{ border-collapse: collapse; width: 100%; max-width: 900px; }}
            th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #eee; }}
            th {{ font-weight: 600; }}
            a {{ text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            </style>
            </head>
            <body>
            <h1>Listing for {prefix}</h1>
            <div>Generated at {now}</div>
            <table>
            <thead><tr><th>Name</th><th>Size</th><th>Last Modified</th></tr></thead>
            <tbody>
        """
        for obj in objects:
            name = obj["name"]
            url = obj["url"]
            size = obj.get("size", "")
            last_modified = obj.get("last_modified", "")
            html += f"<tr><td><a href='{url}'>{name}</a></td><td>{size}</td><td>{last_modified}</td></tr>\n"

        html += "</tbody></table></body></html>"
        return html
    except Exception as e:
        logging.error(f"Error generating index HTML: {e}")
        return ""


def human_size(num):
    """Convert a file size to a human-readable format.

    Args:
        num (int): The file size in bytes.

    Returns:
        str: The human-readable file size.
    """
    try:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if num < 1024.0:
                return f"{num:.0f} {unit}"
            num /= 1024.0
        return f"{num:.0f} PB"
    except Exception as e:
        logging.error(f"Error converting size: {e}")
        return num
