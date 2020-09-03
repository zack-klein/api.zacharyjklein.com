from flask_restplus import Namespace, Resource, reqparse

from northface import handlers


api = Namespace("resumayday", description="Let's find your next job.")
parser = reqparse.RequestParser()
parser.add_argument("job_title", type=str, help="The title of a job.")
parser.add_argument(
    "location", type=str, help="The name or zip code of a location."
)


@api.route("/")
@api.expect(parser)
class Resumayday(Resource):
    def get(self):
        """
        Find a job.
        """
        args = parser.parse_args()
        query = {
            "resource": "resumayday",
            "action": "fetch_jobs_w_keywords",
            "params": {
                "job_title": args["job_title"],
                "location": args["location"],
            },
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response


@api.route("/jobs/")
@api.expect(parser)
class ResumaydayJobs(Resource):
    def get(self):
        """
        Find a job.
        """
        args = parser.parse_args()
        query = {
            "resource": "resumayday",
            "action": "fetch_jobs",
            "params": {
                "job_title": args["job_title"],
                "location": args["location"],
            },
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response


@api.route("/keywords/")
@api.expect(parser)
class ResumaydayKeywords(Resource):
    def get(self):
        """
        Get keywords related to a job.
        """
        args = parser.parse_args()
        query = {
            "resource": "resumayday",
            "action": "fetch_keywords",
            "params": {
                "job_title": args["job_title"],
                "location": args["location"],
            },
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response
