import boto3
import logging
import requests
import tempfile


def parse_uri(path):
    parts = path.replace("s3://", "").split("/")
    bucket = parts.pop(0)
    key = "/".join(parts)
    return bucket, key


def upload_file(path, uri):
    """Upload a file to an S3 bucket

    :param path: File to upload
    :param uri: S3 uri (s3://bucket/key.csv)
    """
    s3 = boto3.client("s3", region_name="us-east-1")
    bucket, key = parse_uri(uri)
    return s3.upload_file(path, bucket, key)


def download_file(uri, path):
    """Download a file from an S3 bucket

    :param uri: S3 uri (s3://bucket/key.csv)
    :param path: Path to download to
    """
    s3 = boto3.client("s3", region_name="us-east-1")
    bucket, key = parse_uri(uri)
    return s3.download_file(bucket, key, path)


def list_keys(uri):
    """
    List all the files in a given URI.
    """
    logging.warning("list_keys is deprecated! Use list_files instead.")
    keys = list_files(uri)
    return keys


def list_files(uri):
    """
    List all the files in a given URI.
    """
    s3 = boto3.client("s3", region_name="us-east-1")
    bucket, key = parse_uri(uri)
    response = s3.list_objects_v2(Bucket=bucket, Prefix=key)
    if key is not None:
        keys = [obj["Key"] for obj in response.get("Contents")]
    else:
        keys = []
    return keys


def get_file(uri):
    """
    Read data from a file in S3.

    :param str bucket: Name of the S3 bucket.
    :param str key: Name of the key.
    """
    s3 = boto3.resource("s3", region_name="us-east-1")
    bucket, key = parse_uri(uri)
    obj = s3.Object(bucket, key)
    body = obj.get()["Body"]
    return body


def request_to_blob(url, uri, params=None):
    """
    Make a GET request, save the Response.text to S3.

    :param str url: The URL to GET.
    :param str uri: The S3 URI to save the data to.
    """
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"Response was: {response}, not 200!")

    with tempfile.NamedTemporaryFile() as fp:
        fp.write(response.text.encode())
        fp.seek(0)
        response = upload_file(fp.name, uri)

    return response
