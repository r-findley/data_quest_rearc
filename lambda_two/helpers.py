import pandas as pd


def trim_whitespace_from_df(df: pd.DataFrame) -> pd.DataFrame:
    """Trims whitespace from column names and string values in a DataFrame.

    Args:
        df (pd.DataFrame): Pandas Dataframe from which to trim whitespace.

    Returns:
        pd.DataFrame: Cleaned Pandas DataFrame with whitespace removed from column names and string values.
    """
    try:
        df.columns = df.columns.str.strip()
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    except TypeError as e:
        print(f"Data passed was not a DataFrame: {e}")
        return df


def get_file_from_bucket(s3_client, bucket_name: str, key: str) -> object:
    """Retrieves a file from an S3 bucket.

    Args:
        s3_client: Boto3 S3 client.
        bucket_name (str): Name of the S3 bucket.
        key (str): Key of the file to retrieve.

    Returns:
        bytes: Content of the file as bytes.
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        print(f"Error retrieving file from bucket: {e}")
        return ""
