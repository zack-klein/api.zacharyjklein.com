from flask_restplus import Namespace, Resource

from northface import handlers


api = Namespace(
    "stopspendingzack",
    description="Bother Zack for spending too much in AWS/GCP.",
)


@api.route("/")
class WhatsMyBill(Resource):
    def post(self):
        """
        Post your bill to slack.
        """
        query = {
            "resource": "whatsmybill",
            "action": "post_bill_slack",
            "params": {},
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response
