import json
import logging
import os
import pandas as pd

from northface.utils import blob

COUNTRY = "US"

# Destination is driven by environmnet variables.
provider = os.environ.get("CLOUD_SERVICE_PROVIDER", "aws")

if provider == "gcp":
    EXTRACT_URI = "gs://snowbird-data/openaq/raw"
    TRANSFORM_URI = "gs://snowbird-data/openaq/clean"

elif provider == "aws":
    EXTRACT_URI = "s3://snowbird-assets/openaq/raw"
    TRANSFORM_URI = "s3://snowbird-assets/openaq/clean"

OPENAQ_API = "https://api.openaq.org/v1/measurements"


def extract(
    date_string,
    url=OPENAQ_API,
    file_type=".json",
    out_uri=EXTRACT_URI,
    country=COUNTRY,
):
    """
    Extract the data from Open AQ's API.

    :param str date_string: The date you want to extract as a string
                            ('%Y-%m-%d').
    """
    out_uri = os.path.join(out_uri, date_string + file_type)
    params = {
        "date_from": date_string,
        "date_to": date_string,
        "country": country,
    }
    blob.request_to_blob(url, out_uri, params=params)
    return out_uri


def transform(
    date_string, file_type=".json", in_uri=EXTRACT_URI, out_uri=TRANSFORM_URI,
):
    """
    Clean up the raw JSON data.
    """
    in_uri = os.path.join(in_uri, date_string + file_type)
    fi = blob.read_file(in_uri)
    # TODO: maybe handle non-results gracefully?
    results = json.loads(fi)["results"]
    raw_df = pd.DataFrame(results)

    if raw_df.empty:
        logging.warning(f"Data from {in_uri} is empty! Exiting gracefully...")
        return "No data today!"

    # Flatten the results
    json_struct = json.loads(raw_df.to_json(orient="records"))
    df_flat = pd.json_normalize(json_struct)

    # Rename some columns - not really necessary, mainly semantic
    df_flat["dateutc"] = df_flat["date.utc"]
    df_flat["datelocal"] = df_flat["date.local"]
    df_flat["latitude"] = df_flat["coordinates.latitude"]
    df_flat["longitude"] = df_flat["coordinates.longitude"]

    del df_flat["date.utc"]
    del df_flat["date.local"]
    del df_flat["coordinates.latitude"]
    del df_flat["coordinates.longitude"]

    # Write it back out to blob storage
    out_uri = os.path.join(out_uri, date_string + file_type)
    df_flat.to_csv(out_uri, index=False)
    return out_uri
