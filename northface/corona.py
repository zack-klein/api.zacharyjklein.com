"""
Extract, transform, and load COVID-19 data from John's Hopkins.
"""

import json
import logging
import os
import pandas as pd
import plotly
import plotly.graph_objs as go
import plotly.express as px

from datetime import datetime
from tqdm import tqdm

from northface.utils import blob

# Destination is driven by environmnet variables.
provider = os.environ.get("CLOUD_SERVICE_PROVIDER", "aws")

if provider == "gcp":
    EXTRACT_URI = "gs://snowbird-data/corona/raw"
    CLEAN_URI = "gs://snowbird-data/corona/clean"

elif provider == "aws":
    EXTRACT_URI = "s3://snowbird-assets/corona/raw"
    CLEAN_URI = "s3://snowbird-assets/corona/clean"


GITHUB_BASE_URL = (
    "https://raw.githubusercontent.com/"
    "CSSEGISandData/COVID-19/master/"
    "csse_covid_19_data/csse_covid_19_daily_reports"
)

RENAME_COLUMNS = {
    "Country/Region": "region",
    "Country_Region": "region",
    "Province_State": "state",
    "Province/State": "state",
    "Last Update": "last_update",
    "Last_Update": "last_update",
    "Lat": "lat",
    "Latitude": "lat",
    "Long_": "lon",
    "Longitude": "lon",
    "Confirmed": "confirmed",
    "Deaths": "deaths",
    "Recovered": "recovered",
}

DEFAULT_TYPE_COLUMNS = {
    "state": "object",
    "region": "object",
    "last_update": "datetime64",
    "confirmed": "float",
    "deaths": "float",
    "recovered": "float",
    "dt": "object",
    "lat": "object",
    "lon": "object",
}

RENAME_REGION_VALUES = {
    "Mainland China": "China",
    "Korea, South": "South Korea",
    "Republic of Korea": "South Korea",
}

LATLON_CLEANUP_VALUES = {0: ""}


def extract(
    date_string,
    base_url=GITHUB_BASE_URL,
    file_type=".csv",
    out_uri=EXTRACT_URI,
):
    """
    Extract the data from Github.

    :param str date_string: The date you want to extract as a string
                            ('%m-%d-%Y').
    """
    # Get the file
    request_url = os.path.join(base_url, date_string + file_type)
    out_uri = os.path.join(out_uri, date_string + file_type)
    blob.request_to_blob(request_url, out_uri)
    return out_uri


def rename_df(df, column_mapping=RENAME_COLUMNS, hard=False):
    """
    Rename the columns of a Dataframe

    :param pandas.DataFrame df: Pandas df.
    :param dict column_mapping: Dictionary of column Name:Rename
    :param bool hard: Delete columns not in the mapping if they don't exist.
    :return pandas.DataFrame: Df of renamed columns
    """

    for column in df.columns:
        if column in column_mapping.keys():
            new_name = column_mapping[column]
            df[new_name] = df[column]

        if hard:
            del df[column]

    return df


def add_columns(df, column_mapping=RENAME_COLUMNS):
    """
    Add columns that don't exist to a pandas Dataframe.

    :param pandas.DataFrame df: Pandas df.
    :param dict column_mapping: Dictionary of column Name:Rename
    """

    for column in set(column_mapping.values()):
        if column not in df.columns:
            df[column] = ""

    return df


def rename_regions(
    df, column_mapping=RENAME_REGION_VALUES, region_column="region"
):
    """
    Rename values in the `region` column.

    :param pandas.DataFrame df: DF with a `region` column.
    :param dict column_mapping: Dict of {"Old Name": "New Name"}
    """

    for old_name, new_name in column_mapping.items():
        df[region_column] = df[region_column].replace(old_name, new_name)

    return df


def clean_latlon(
    df,
    lat_lon_replacements=LATLON_CLEANUP_VALUES,
    lat_lon_columns=["lat", "lon"],
):
    """
    Clean up latitude and longitude columns.

    :param pandas.DataFrame df: DF with a `region` column.
    :param dict column_mapping: Dict of {"Old Val": "New Val"}
    """

    for column in lat_lon_columns:
        for old_value, new_value in lat_lon_replacements.items():
            df[column] = df[column].replace(old_value, new_value)

    return df


def transform(
    date_string,
    in_uri=EXTRACT_URI,
    out_uri=CLEAN_URI,
    ts_column_name="dt",
    as_types=DEFAULT_TYPE_COLUMNS,
    rename_columns=RENAME_COLUMNS,
    rename_regions_columns=RENAME_REGION_VALUES,
    file_type=".csv",
):
    """
    Read a file from cloud storage into a pandas df, add a column with the
    timestamp,and write it back to cloud storage.

    :param str date_string: The date you want to extract as a string
                            ('%m-%d-%Y').
    """
    in_uri = os.path.join(in_uri, date_string + file_type)
    logging.info(f"Reading from {in_uri}...")
    df = pd.read_csv(in_uri)

    filtered_df = rename_df(df, column_mapping=rename_columns, hard=True)
    filtered_df = add_columns(df, column_mapping=rename_columns)
    filtered_df = clean_latlon(df, lat_lon_replacements=LATLON_CLEANUP_VALUES)
    filtered_df = rename_regions(df, column_mapping=rename_regions_columns)
    filtered_df[ts_column_name] = datetime.strptime(
        date_string, "%m-%d-%Y"
    ).strftime(
        "%Y-%m-%d"
    )  # TODO: Standardize this

    if as_types:
        filtered_df.astype(as_types)

    out_uri = os.path.join(out_uri, date_string + file_type)
    logging.info(f"Writing to {out_uri}...")
    filtered_df.to_csv(out_uri, index=False)

    return out_uri


def fetch_data(date=None, base_uri=CLEAN_URI, file_type=".csv"):
    """
    Get all of the coronavirus data that's been uploaded.

    :param str date: String of the date ('%m-%d-%Y').
    :param str base_uri: The base uri to build the path on.
    :param str file_type: CSV. Should probably never change.
    """
    if not date:
        keys = blob.list_files(base_uri)
    else:
        keys = [os.path.join("corona/clean", date + file_type)]  # TODO: fix
    dfs = []
    logging.info("Reading in Coronavirus data...")
    for key in tqdm(keys):
        path = os.path.join(base_uri, os.path.basename(key))
        dfs.append(pd.read_csv(path))
    df = pd.concat(dfs)
    df.reset_index(drop=True, inplace=True)
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


def fetch_data_graphable(date=None, base_uri=CLEAN_URI):
    """
    Build a dataframe of graph-friendly data.
    """
    df = pd.DataFrame(fetch_data(date=date, base_uri=base_uri))
    df["recovered_pcent"] = (df["recovered"] / df["confirmed"]) * 100
    df["deaths_pcent"] = (df["deaths"] / df["confirmed"]) * 100
    df["active"] = df["confirmed"] - (df["deaths"] + df["recovered"])
    df["active_pcent"] = (df["active"] / df["confirmed"]) * 100
    df.sort_values(["dt"], ascending=True)
    return df


def create_map(df, country=None):
    """
    Create a graphable JSON Map object.
    """
    if country:
        df = df[df["region"].isin(country)]
        if True in list(pd.isna(df["state"])):
            hover_name = color = text = df["region"]
        else:
            hover_name = color = text = df["state"]
            if len(hover_name.unique()) == 1:
                hover_name = color = text = df["region"]

    else:
        hover_name = color = text = df["region"]
        country = "Whole World"

    natearth_fig = px.scatter_geo(
        df,
        lat=df["lat"],
        lon=df["lon"],
        labels=df["confirmed"],
        hover_name=hover_name,
        text=text,
        size=df["confirmed"],
        color=color,
        projection="natural earth",
    )

    natearth_fig.update_layout(
        showlegend=False,  # title=f"Globe View of the {country}",
    )
    natearth_fig.update_geos(fitbounds="locations")

    graphJSON = json.dumps(natearth_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


# Table - only needs today's data
def create_table(df, nrows=10, country=None, y_axis="dt"):
    """
    Create a graphable table of statistics object.
    """
    if country:
        df = df[df["region"].isin(country)]
    else:
        df = df[df["confirmed"] > 1000]
        country = "Whole World"

    df = df.groupby(["state", "region", "dt"]).sum().reset_index()

    df["recovered_pcent"] = ((df["recovered"] / df["confirmed"]) * 100).round(
        1
    )
    df["deaths_pcent"] = ((df["deaths"] / df["confirmed"]) * 100).round(1)
    df["active"] = df["confirmed"] - (df["deaths"] + df["recovered"])
    df["active_pcent"] = ((df["active"] / df["confirmed"]) * 100).round(1)
    df = df.sort_values([y_axis], ascending=False)
    df = df[
        [
            "state",
            "region",
            "confirmed",
            "deaths",
            "recovered",
            "active",
            "recovered_pcent",
            "deaths_pcent",
            "active_pcent",
        ]
    ]
    df.columns = [
        "State",
        "Region",
        "Confirmed",
        "Deaths",
        "Recovered",
        "Active",
        "Recovered (%)",
        "Deaths (%)",
        "Active (%)",
    ]
    df.dropna(inplace=True)
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=list(df.columns), align="left"),
                cells=dict(
                    values=[
                        df["State"],
                        df["Region"],
                        df["Confirmed"],
                        df["Deaths"],
                        df["Recovered"],
                        df["Active"],
                        df["Recovered (%)"],
                        df["Deaths (%)"],
                        df["Active (%)"],
                    ],
                    align="left",
                ),
            )
        ],
        layout=go.Layout(
            margin=go.layout.Margin(l=0, r=0, b=0, t=0)  # noqa:E741
        ),
    )
    serialized = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return serialized


# Time series - needs the whole dataframe
def create_chart(df, country=None, chart_type="lines", y_axis="deaths_pcent"):
    """
    """
    if country:
        df = df[df["region"].isin(country)]
    else:
        df = df[df["confirmed"] > 1000]
        country = "Whole World"

    dr_data = []

    for region in df.region.unique():
        relevant = df[df["region"] == region]
        relevant.sort_values(by="dt")
        d = {
            "x": relevant["dt"],
            "y": relevant[y_axis],
            "text": relevant[y_axis],
            "mode": chart_type,
            "marker": {"size": 15, "line": {"width": 0.5, "color": "white"}},
            "name": region,
        }
        dr_data.append(d)

    fig = go.Figure(
        data=dr_data,
        layout=go.Layout(
            showlegend=False,
            transition={"duration": 500},
            # title=f"{y_axis.title()} of the {country} Over Time",
            margin=go.layout.Margin(l=5, r=5, b=5, t=5),  # noqa:E741
        ),
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


# API entry point
def fetch_plots(
    country=None, chart_type=None, y_axis="deaths_pcent", base_uri=CLEAN_URI
):
    """
    Create the plots in an entry point.
    """
    most_recent_date = datetime.strptime(
        get_most_recent_date(), "%m/%d/%Y"
    ).strftime("%m-%d-%Y")

    if os.environ.get("LOCAL"):
        all_data_date = most_recent_date
    else:
        all_data_date = None

    # Data
    all_data = fetch_data_graphable(date=all_data_date, base_uri=base_uri)
    all_data_grouped = (
        all_data.groupby(["region", "dt"])
        .sum()
        .sort_values(["dt"], ascending=False)
        .reset_index()
    )
    todays_data = fetch_data_graphable(
        date=most_recent_date, base_uri=base_uri
    )

    # Plots
    map = create_map(all_data_grouped, country=country)  # needs today's
    chart = create_chart(
        all_data, country=country, chart_type=chart_type, y_axis=y_axis
    )  # needs whole thing
    stats = create_table(
        todays_data, country=country, y_axis=y_axis
    )  # needs today's
    obj = json.dumps((map, chart, stats))
    return obj
