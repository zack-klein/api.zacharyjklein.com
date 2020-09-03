import boto3
import base64
import json
import os


def get_secret(secret_name):
    """
    Grab a secret

    :param str secret_name: Name of the secret in secrets manager.
    :return dict: Dict of the secret.
    """
    region_name = "us-east-1"
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager", region_name=region_name
    )
    response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in response:
        secret = response["SecretString"]
    else:
        secret = base64.b64decode(response["SecretBinary"])

    return secret


def secret_to_env(secret_name):
    """
    Grab a secret and turn it into environment variables.
    """

    secret_d = json.loads(get_secret(secret_name))
    for name, value in secret_d.items():
        os.environ[name] = value
