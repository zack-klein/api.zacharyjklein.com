"""Utilities for logging in with Cognito.
"""
import boto3
import logging


def login(user, password, pool_id, client_id):
    """Try getting authentication keys.
    """
    success = False
    try:
        _get_auth_keys(user, password, pool_id, client_id)
        success = True
    except Exception:
        logging.info("Invalid username and password!")
    return success


def _get_auth_keys(user, password, pool_id, client_id):
    """Get authentication keys given a user and password.
    """
    client = boto3.client("cognito-idp")
    response = client.admin_initiate_auth(
        UserPoolId=pool_id,
        ClientId=client_id,
        AuthFlow="ADMIN_NO_SRP_AUTH",
        AuthParameters={"USERNAME": user, "PASSWORD": password},
    )
    auth_keys = response.get("AuthenticationResult")
    return auth_keys
