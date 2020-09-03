"""
Presidential polling data analysis.
"""

import os
import pandas as pd

from northface.utils import blob


# Destination is driven by environmnet variables.
provider = os.environ.get("CLOUD_SERVICE_PROVIDER", "aws")

if provider == "gcp":
    EXTRACT_URI = "gs://snowbird-data/pollin/raw"
    CLEAN_URI = "gs://snowbird-data/pollin/clean"

elif provider == "aws":
    EXTRACT_URI = "s3://snowbird-assets/pollin/raw"
    CLEAN_URI = "s3://snowbird-assets/pollin/clean"


URL = "https://projects.fivethirtyeight.com/polls-page/president_polls.csv"


def extract(date_string, base_uri=EXTRACT_URI, url=URL, file_type=".csv"):
    """
    Extract data from FiveThirtyEight and save it to cloud storage.
    """
    uri = os.path.join(base_uri, date_string + file_type)
    blob.request_to_blob(url, uri)
    return uri


def transform(
    date_string,
    in_uri_base=EXTRACT_URI,
    out_uri_base=CLEAN_URI,
    file_type=".csv",
):
    """
    Add a `dt` column to the data and save it back to cloud storage.
    """
    in_uri = os.path.join(in_uri_base, date_string + file_type)

    df = pd.read_csv(in_uri)
    df["dt"] = date_string
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["created_at"] = df["created_at"].dt.strftime("%m-%d-%Y")

    out_uri = os.path.join(out_uri_base, date_string + file_type)
    df.to_csv(out_uri)
    return out_uri


def fetch_data(base_uri=CLEAN_URI):
    """
    Grab most recent data from cloud storage.
    """
    keys = blob.list_files(base_uri)
    dt = max([os.path.splitext(os.path.basename(k))[0] for k in keys])
    clean_data_path = f"{base_uri}/{dt}.csv"
    df = pd.read_csv(clean_data_path)
    return df.to_dict()


def get_most_recent_date(base_uri=CLEAN_URI):
    """
    Get the most recent day that data was loaded based on a URI.
    """
    keys = blob.list_files(base_uri)
    dt = max([os.path.splitext(os.path.basename(k))[0] for k in keys]).replace(
        "-", "/"
    )
    return dt
