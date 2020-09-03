"""
Utilities for dealing with Google Cloud Datastore.

Great docs on this:
https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/datastore/cloud-client/tasks.py
"""

from google.cloud import datastore


def add_item(kind, name, item):
    """
    Add item to GCP Cloud Datastore.

    :param str kind: The kind of entity to add.
    :param str name: The unique name for the client.
    :param dict item: Arbitrary key-value pairs to add as an item.
    """
    client = datastore.Client()
    task_key = client.key(kind, name)
    entity = datastore.Entity(key=task_key)

    for key, value in item.items():
        entity[key] = value

    response = client.put(entity)

    return response


def update_item(kind, name, update_dict):
    """
    Update an item in GCP Cloud Datastore.

    :param str kind: The kind of entity to add.
    :param str name: The unique name for the client.
    :param dict update_dict: Dict of what the new item should look like.
    """
    client = datastore.Client()
    with client.transaction():
        key = client.key(kind, name)
        item = client.get(key)

        if not item:
            raise ValueError("Task {} does not exist.".format(key))

        item.update(update_dict)

        response = client.put(item)
    return response


def delete_item(kind, name):
    """
    Delete item from GCP Cloud Datastore.

    :param str kind: The kind of entity to add.
    :param str name: The unique name for the client.
    """
    client = datastore.Client()
    key = client.key(kind, name)
    response = client.delete(key)
    return response


def scan(kind, key_name="key", order=None):
    """
    Scan for items in GCP Cloud Datastore.

    :param str kind: The kind of entity to add.
    :param str key_name: Name of the key column.
    :param str order: Order the results?
    """
    client = datastore.Client()
    query = client.query(kind=kind)

    if order:
        query.order = [order]

    rows = list(query.fetch())

    # Add the key to the results. This will hurt performance, but YOLO.
    items = []

    for row in rows:
        item = dict(row)
        item[key_name] = row.key.name
        items.append(item)

    return items
