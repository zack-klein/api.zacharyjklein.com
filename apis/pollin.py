from flask_restplus import Namespace, Resource

from northface import handlers


api = Namespace("pollin", description="Pollin' for president endpoint.")


@api.route("/")
class Pollin(Resource):
    def get(self):
        """
        Get the most recent data for the Coronavirus from John's Hopkins.
        """
        query = {
            "resource": "pollin",
            "action": "fetch_data",
            "params": {},
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response


@api.route("/date")
class PollinDate(Resource):
    def get(self):
        """
        Get the updated date for the Coronavirus from John's Hopkins.
        """
        query = {
            "resource": "pollin",
            "action": "get_most_recent_date",
            "params": {},
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response
