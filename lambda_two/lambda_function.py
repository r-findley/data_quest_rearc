import logging
import os
import boto3
import pandas as pd
import io
import json
from helpers import (
    get_file_from_bucket,
    trim_whitespace_from_df,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_two_handler(event, context):
    for record in event.get("Records", []):
        logger.info(f"Lambda two triggered by {record}")
    bucket_name = os.environ["BUCKET_NAME"]
    s3_client = boto3.client("s3")
    bls_file = "bls_data/pr.data.0.Current"
    population_data = "datausa/datausa_population.json"
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    try:
        bls_csv = get_file_from_bucket(
            s3_client=s3_client, bucket_name=bucket_name, key=bls_file
        )
        logger.info("Retrieved BLS data from S3")
        population_json = get_file_from_bucket(
            s3_client=s3_client, bucket_name=bucket_name, key=population_data
        )
    except Exception as e:
        logger.error(f"Unable to retrieve files from S3 - {e}", exc_info=True)
        return

    if bls_csv:
        logger.info(f"Type of bls_csv: {type(bls_csv)}")
        bls_df = pd.read_csv(io.StringIO(bls_csv), sep="\t")
        bls_df = trim_whitespace_from_df(bls_df)
        bls_df.columns = bls_df.columns.str.capitalize()
        logger.info(f"BLS DataFrame loaded with {len(bls_df)} records")

    if population_json:
        logger.info(f"Type of population_json: {type(population_json)}")
        population_data = json.loads(population_json)
        population_df = pd.json_normalize(population_data, record_path=["data"])
        population_df = trim_whitespace_from_df(population_df)
        population_df["Population"] = population_df["Population"].astype(int)

    try:
        filtered_population_df = population_df[
            (population_df["Year"] >= 2013) & (population_df["Year"] <= 2018)
        ]
        mean_population = filtered_population_df["Population"].mean()
        standard_deviation = filtered_population_df["Population"].std()
        logger.info(f"Mean Population (2013-2018): {int(mean_population):,}")
        logger.info(f"Standard Deviation (2013-2018): {int(standard_deviation):,}")
    except Exception as e:
        logger.error(f"Error calculating population statistics - {e}", exc_info=True)

    try:
        series_grouped = (
            bls_df.groupby(["Series_id", "Year"])["Value"].sum().reset_index()
        )
        best_years_idx = series_grouped.groupby("Series_id")["Value"].idxmax()
        best_years_for_each_series = series_grouped.loc[
            best_years_idx, ["Series_id", "Year", "Value"]
        ]
        logger.info(
            f"Best years for each series calculated, total records: {best_years_for_each_series=}"
        )
    except Exception as e:
        logger.error(
            f"Error determining best years for each series - {e}", exc_info=True
        )

    try:
        series_PRS30006032_data = bls_df.loc[
            (bls_df["Series_id"] == "PRS30006032") & (bls_df["Period"] == "Q01")
        ]
        concatenated_df = series_PRS30006032_data.merge(
            population_df, on="Year", how="inner"
        )
        concatenated_df = concatenated_df.drop(
            columns=["Footnote_codes", "Nation ID", "Nation"]
        )
        concatenated_df = concatenated_df.rename(
            columns={
                "Value": "value",
                "Year": "year",
                "Series_id": "series",
                "Period": "period",
            }
        )
        logger.info(f"Concatenated Population and Series Dataframe: {concatenated_df=}")
    except Exception as e:
        logger.error(f"Error merging population and series data - {e}", exc_info=True)
