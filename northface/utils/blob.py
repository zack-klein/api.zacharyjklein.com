"""
Utilities for interacting with cloud blob storage. Allows for URI-based
handling of files across cloud providers.
"""

from northface.utils import gcs, s3


MODULE_MAPPING = {
    "gs": gcs,
    "s3": s3,
}


def get_destination_module(destination, mapping=MODULE_MAPPING):
    """
    Check that a module exists, return it if it does.
    """
    if destination not in mapping:
        raise ValueError(
            f"'{destination}' is not a supported destination! Supported are: "
            f"{', '.join(list(mapping.keys()))}"
        )
    else:
        return mapping[destination]


def upload_file(path, uri, mapping=MODULE_MAPPING):
    """
    Upload a file to cloud storage.
    """
    destination = uri[:2]
    module = get_destination_module(destination)
    response = module.upload_file(path, uri)
    return response


def download_file(uri, path, mapping=MODULE_MAPPING):
    """
    Download a file from cloud storage.
    """
    destination = uri[:2]
    module = get_destination_module(destination)
    response = module.download_file(uri, path)
    return response


def list_files(uri):
    """
    List files in cloud storage.
    """
    destination = uri[:2]
    module = get_destination_module(destination)
    response = module.list_files(uri)
    return response


def request_to_blob(url, uri, params=None):
    """
    Run a GET request, save the result to S3.
    """
    destination = uri[:2]
    module = get_destination_module(destination)
    response = module.request_to_blob(url, uri, params=params)
    return response


def read_file(uri):
    """
    Read a file from blob storage.
    """
    destination = uri[:2]
    module = get_destination_module(destination)
    response = module.read_file(uri)
    return response
