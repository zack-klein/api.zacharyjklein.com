import requests
import tempfile

from google.cloud import storage


def parse_uri(uri):
    parts = uri.replace("gs://", "").split("/")
    bucket = parts.pop(0)
    blob = "/".join(parts)
    return bucket, blob


def upload_file(path, uri):
    """
    Uploads a file to the bucket.
    """
    storage_client = storage.Client()
    bucket_name, destination_blob_name = parse_uri(uri)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    return blob.upload_from_filename(path)


def download_file(uri, path):
    """
    Downloads a blob from the bucket.
    """
    storage_client = storage.Client()
    bucket_name, source_blob_name = parse_uri(uri)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    return blob.download_to_filename(path)


def list_files(uri, delimiter=None):
    """
    Lists all the blobs in the bucket.
    """
    storage_client = storage.Client()
    bucket_name, prefix = parse_uri(uri)
    blobs = storage_client.list_blobs(
        bucket_name, prefix=prefix, delimiter=delimiter
    )
    return [blob.name for blob in blobs]


def request_to_blob(url, uri, params=None):
    """
    Make a GET request, save the Response.text to GS.

    :param str url: The URL to GET.
    :param str uri: The GS URI to save the data to.
    """
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"Response was: {response}, not 200!")

    with tempfile.NamedTemporaryFile() as fp:
        fp.write(response.text.encode())
        fp.seek(0)
        response = upload_file(fp.name, uri)

    return response


def read_file(uri):
    """
    Read the contents of a blob file in GCS.

    :param str url: The URL to GET.
    :return str: The text of the file.
    """
    storage_client = storage.Client()
    bucket_name, prefix = parse_uri(uri)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.get_blob(prefix)
    text = blob.download_as_string()
    return text
