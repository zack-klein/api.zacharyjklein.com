import logging
import datetime

from flask import request
from flask_restplus import Namespace, Resource

from northface import handlers

api = Namespace("api", description="Legacy way to interact with Snowbird API.")


@api.route("/v1.0/")
class LegacyAPIRequest(Resource):
    def get(self):
        return f"Healthy at {datetime.datetime.now().isoformat()}!"

    def post(self):
        """Run an action on a resource."""
        logging.warning("The /api/v1.0 endpoint is deprecated!")
        if (
            not request.json
            or "resource" not in request.json
            or "action" not in request.json
            or "params" not in request.json
        ):
            api.abort(
                code=400,
                message=(
                    "Invalid request! Must be resource, action, params. "
                    f"Received: {request.json}"
                ),
            )
        query = {
            "resource": request.json["resource"],
            "action": request.json["action"],
            "params": request.json.get("params", {}),
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response
