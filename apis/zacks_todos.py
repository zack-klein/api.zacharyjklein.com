from flask_restplus import Namespace, Resource, reqparse

from northface import handlers


api = Namespace(
    "zacks_todos", description="Every developer's first application.",
)


@api.route("/")
class Todos(Resource):
    def get(self):
        """
        Get todos from
        """
        query = {
            "resource": "zacks_todos",
            "action": "read",
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
add_parser.add_argument("todo", type=str, help="The todo item.")
add_parser.add_argument(
    "author", type=str, help="The name of the author of the todo."
)
add_parser.add_argument("category", type=str, help="Category for the todo.")


@api.route("/add_todo")
@api.expect(add_parser)
class AddTodos(Resource):
    def post(self):
        """
        Get all the todos from the table.
        """
        args = add_parser.parse_args()
        query = {
            "resource": "zacks_todos",
            "action": "create",
            "params": {
                "todo": args["todo"],
                "author": args["author"],
                "category": args["category"],
                "done": False,
            },
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response


id_parser = reqparse.RequestParser()
id_parser.add_argument("id", type=str, help="The ID of the todo.")


@api.route("/toggle_complete")
@api.expect(id_parser)
class ToglleTodoComplete(Resource):
    def post(self):
        """
        Toggle a todo complete.
        """
        args = id_parser.parse_args()
        query = {
            "resource": "zacks_todos",
            "action": "toggle_complete",
            "params": {"id": args["id"]},
        }
        try:
            response = handlers.dict_handler(query)
        except Exception as e:
            api.abort(
                code=500, message=f"The code ran, but there was an error: {e}"
            )
        return response


@api.route("/delete")
@api.expect(id_parser)
class DeleteTodo(Resource):
    def post(self):
        """
        Toggle a todo complete.
        """
        args = id_parser.parse_args()
        query = {
            "resource": "zacks_todos",
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
