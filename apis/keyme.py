from flask_restplus import Namespace, Resource, reqparse

from northface import handlers


api = Namespace("keyme", description="Grab keywords from text!")
parser = reqparse.RequestParser()
parser.add_argument(
    "text", type=str, help="A block of text to extract keywords from."
)


@api.route("/")
@api.expect(parser)
class KeyMe(Resource):
    def get(self):
        """
        Send some text and get keywords back.
        """
        args = parser.parse_args()
        query = {
            "resource": "keyme",
            "action": "get_keywords",
            "params": {"text": args["text"]},
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response
