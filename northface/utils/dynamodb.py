import boto3

from boto3.dynamodb.conditions import Key, Attr


def scan(table_name, filter_key=None, filter=None):
    """Fetch all the items in a table. Can get slow.
    """
    ddb = boto3.resource("dynamodb", region_name="us-east-1")
    table = ddb.Table(table_name)
    if filter_key is not None and filter is not None:
        scan = table.scan(FilterExpression=Attr(filter_key).eq(filter))
    else:
        scan = table.scan()
    items = scan["Items"]
    return items


def query(table_name, key, value):
    """Fetch only some items in a table.
    """
    ddb = boto3.resource("dynamodb", region_name="us-east-1")
    table = ddb.Table(table_name)
    response = table.query(KeyConditionExpression=Key(key).eq(value))
    if len(response["Items"]) == 0:
        raise ValueError(f"{key}: {value} not found!")
    else:
        return response["Items"]


def pkey_query(table_name, pkey, pkey_val, skey, skey_val):
    """Query based on the partition key and the sort key.
    """
    ddb = boto3.resource("dynamodb", region_name="us-east-1")
    table = ddb.Table(table_name)
    response = table.query(
        KeyConditionExpression=Key(pkey).eq(pkey_val) & Key(skey).eq(skey_val)
    )
    return response


def index_query(table_name, index_name, key, value, **kwargs):
    """Fetch some items based on a secondary index.
    """
    ddb = boto3.resource("dynamodb", region_name="us-east-1")
    table = ddb.Table(table_name)
    response = table.query(
        IndexName=index_name,
        KeyConditionExpression=Key(key).eq(value),
        **kwargs,
    )
    return response


def add_item(table_name, item):
    """Add to a ddb table.
    """
    ddb = boto3.resource("dynamodb", region_name="us-east-1")
    table = ddb.Table(table_name)
    response = table.put_item(Item=item)
    return response


def update_item(table_name, item_expr, update_expr):
    """Update an item in a ddb table.
    """
    ddb = boto3.resource("dynamodb", region_name="us-east-1")
    table = ddb.Table(table_name)
    response = table.update_item(Key=item_expr, AttributeUpdates=update_expr,)
    return response


def delete_item(table_name, delete_expr):
    """Delete from a ddb table.
    """
    ddb = boto3.resource("dynamodb", region_name="us-east-1")
    table = ddb.Table(table_name)
    response = table.delete_item(Key=delete_expr)
    return response
