from flask_restplus import Namespace, Resource

import datetime


api = Namespace("healthy", description="Health check.")


@api.route("/")
class HealthCheck(Resource):
    def get(self):
        return f"Healthy at {datetime.datetime.now().isoformat()}!"
