from flask_restplus import Namespace, Resource, reqparse

from northface import handlers


api = Namespace(
    "nurse", description="Backend for health checking, simplified.",
)


@api.route("/")
class HealthCheck(Resource):
    def get(self):
        """
        Get all available health checks.
        """
        query = {
            "resource": "nurse",
            "action": "get",
            "params": {},
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response


add_parser = reqparse.RequestParser()
add_parser.add_argument("site", type=str, help="The name of the site checked.")
add_parser.add_argument("healthy", type=bool, help="Is the site healthy?")


@api.route("/add_health_check")
@api.expect(add_parser)
class AddHealthCheck(Resource):
    def post(self):
        """
        Add a health check to the table.
        """
        args = add_parser.parse_args()
        query = {
            "resource": "nurse",
            "action": "add",
            "params": {"site": args["site"], "healthy": args["healthy"]},
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response


id_parser = reqparse.RequestParser()
id_parser.add_argument(
    "id", type=str, help="The ID of the health_check to delete."
)


@api.route("/delete_health_check")
@api.expect(id_parser)
class DeleteHealthCheck(Resource):
    def delete(self):
        """
        Delete a
        """
        args = id_parser.parse_args()
        query = {
            "resource": "nurse",
            "action": "delete",
            "params": {"id": args["id"]},
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response
