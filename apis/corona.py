from flask_restplus import Namespace, Resource

from northface import handlers


api = Namespace("corona", description="Coronavirus endpoint.")


@api.route("/")
class Corona(Resource):
    def get(self):
        """
        Get the most recent data for the Coronavirus from John's Hopkins.
        """
        query = {
            "resource": "corona",
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
class CoronaDate(Resource):
    def get(self):
        """
        Get the updated date for the Coronavirus from John's Hopkins.
        """
        query = {
            "resource": "corona",
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


@api.route("/plots")
class CoronaPlots(Resource):
    def get(self):
        """
        Get the updated date for the Coronavirus from John's Hopkins.
        """
        query = {
            "resource": "corona",
            "action": "fetch_plots",
            "params": {},
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response
