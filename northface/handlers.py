import argparse
import inspect
import jana
import json
import logging
import os
import sys

SECRET_NAME = ""


CLOUD_SERVICE_PROVIDER = os.getenv("CLOUD_SERVICE_PROVIDER")

# Across cloud providers, secrets get injected into the application as
# environment variables. Because of this, the application needs to know
# where to look in each environment for the secrets.
SECRET_STRING_NAME = os.getenv("SECRET_STRING_NAME")
GCP_PROJECT_NAME = os.getenv("GCP_PROJECT_NAME")
GCP_SECRET_VERSION = os.getenv("GCP_SECRET_VERSION")


def json_string_to_env(string):
    d = json.loads(string)
    for key, value in d.items():
        os.environ[key] = value


try:
    if CLOUD_SERVICE_PROVIDER == "gcp":
        secret_string = jana.fetch_secret(
            "gcp-secretmanager",
            SECRET_STRING_NAME,
            GCP_PROJECT_NAME,
            GCP_SECRET_VERSION,
        )
        json_string_to_env(secret_string)

    elif CLOUD_SERVICE_PROVIDER == "aws":
        secret_string = jana.fetch_secret(
            "aws-secretsmanager", SECRET_STRING_NAME,
        )
        json_string_to_env(secret_string)

except Exception as e:
    logging.error(
        f"Tried to read secrets from provider: {CLOUD_SERVICE_PROVIDER} "
        f"but failed with exception: '{e}'! The webserver will attempt to "
        "start, but likely won't function properly because it can't make API "
        "calls."
    )


from northface import (  # noqa
    keyme,
    sentimenter,
    corona,
    pollin,
    whatsmybill,
    resumayday,
    zacks_todos,
    openaq,
    nurse,
)

CLI_LOGO = r"""
               .        .
 __._  _ .    ,|_ *._. _|
_) [ )(_) \/\/ [_)|[  (_]
-------------------------
"""

CLI_DESC = (
    CLI_LOGO
    + r"""
Snowbird CLI
sb <resource> <action> [<args>]
"""
)


def get_name(module):
    return module.__name__.split(".")[-1]


RESOURCES = {
    get_name(keyme): keyme,
    get_name(sentimenter): sentimenter,
    get_name(corona): corona,
    get_name(resumayday): resumayday,
    get_name(pollin): pollin,
    get_name(whatsmybill): whatsmybill,
    get_name(zacks_todos): zacks_todos,
    get_name(openaq): openaq,
    get_name(nurse): nurse,
}


def get_functions(module):
    return {
        f[0]: f[1]
        for f in inspect.getmembers(module)
        if inspect.isfunction(f[1])
    }


def fetch_actions(module):
    """
    Examine a module, and create an argparser from all of its callable
    objects.

    :param module module: A python module
    :return tuple(callable, dict): A function and the args it should use
    """
    module_doc = module.__doc__ or module.__name__
    parser = argparse.ArgumentParser(
        description=CLI_LOGO + module_doc,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    functions = get_functions(module)
    parser.add_argument("action", choices=functions.keys())
    args = parser.parse_args(sys.argv[2:3])

    function = functions[args.action]
    function_doc = function.__doc__ or function.__name__
    subparser = argparse.ArgumentParser(
        description=CLI_LOGO + function_doc,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    params = inspect.signature(function).parameters

    for param_name, param in params.items():
        if param.default is not inspect._empty:
            param_name = "--" + param_name
        subparser.add_argument(param_name)

    subargs = subparser.parse_args(sys.argv[3:])

    function_args = {}
    for param_name in params.keys():
        if getattr(subargs, param_name, None) is not None:
            function_args[param_name] = getattr(subargs, param_name, None)

    return function, function_args


def cli_handler():
    """
    Parse arguments from the command line.
    """
    command_parser = argparse.ArgumentParser(
        description=CLI_DESC,
        usage="sb <resource> <action> [<args>]",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    command_parser.add_argument(
        "resource", help="Command to run", choices=RESOURCES.keys()
    )
    args = command_parser.parse_args(sys.argv[1:2])
    action, params = fetch_actions(RESOURCES[args.resource])
    response = handle(action, params)
    if response is not None:
        print(response)


def dict_handler(d):
    """
    Parse arguments from a dictionary.
    """
    resource = d.get("resource")
    action = d.get("action")
    params = d.get("params")

    if not all([resource, action]) and params is None:
        raise TypeError("Not all resource, action, and params provided!")

    if resource not in RESOURCES.keys():
        raise TypeError(f"Resource {resource} is invalid!")

    actions = get_functions(RESOURCES[resource])

    if action not in actions.keys():
        raise TypeError(f"Action {action} is invalid!")

    action = actions[action]

    if not isinstance(params, dict):
        raise TypeError("Params are invalid! Must be a dict.")

    response = handle(action, params)

    return response


def lambda_handler(event, context):
    """Parse the event and pass it to the application.
    """
    request = json.loads(event["body"])
    result = dict_handler(request)
    response = {}
    response["body"] = json.dumps(result)
    response["headers"] = {"Access-Control-Allow-Origin": "*"}
    return response


def api_handler(request):
    return dict_handler(request)


def handle(function, args):
    return function(**args)
