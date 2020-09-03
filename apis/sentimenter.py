from flask_restplus import Namespace, Resource, reqparse

from northface import handlers


api = Namespace(
    "sentimenter", description="Let's see how the world feels about..."
)
parser = reqparse.RequestParser()
parser.add_argument(
    "text", type=str, help="Some text to get the sentiment of."
)


@api.route("/")
@api.expect(parser)
class SentimenterText(Resource):
    def get(self):
        """
        Get the sentiment of a piece of text.
        """
        args = parser.parse_args()
        query = {
            "resource": "sentimenter",
            "action": "get_sentiment",
            "params": {"text": args["text"]},
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response


tweets_parser = reqparse.RequestParser()
tweets_parser.add_argument("topic", type=str, help="A topic to query.")


@api.route("/tweets/")
@api.expect(tweets_parser)
class SentimenterTweets(Resource):
    def get(self):
        """
        Enter a topic, and see how the world feels about it.
        """
        args = tweets_parser.parse_args()
        query = {
            "resource": "sentimenter",
            "action": "get_tweets",
            "params": {"topic": args["topic"]},
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response
