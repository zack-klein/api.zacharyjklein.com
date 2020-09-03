from flask_restplus import Namespace, Resource, reqparse

from northface import handlers


api = Namespace("openaq", description="Extract data from Open AQ.",)

parser = reqparse.RequestParser()
parser.add_argument("date_string", type=str, help="Date string as YYYY-MM-DD.")


@api.route("/")
@api.expect(parser)
class Extract(Resource):
    def get(self):
        """
        Run the extract.
        """
        args = parser.parse_args()
        query = {
            "resource": "openaq",
            "action": "extract",
            "params": {"date_string": args["date_string"]},
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response
