from northface import handlers


def handle(event, context):
    return handlers.lambda_handler(event, context)
