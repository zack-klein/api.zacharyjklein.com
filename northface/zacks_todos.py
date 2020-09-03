import enum

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app import db


class Categories(enum.Enum):
    DEV = "Development"
    FUN = "Fun"
    OTHER = "Other"
    WORK = "Work"


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String)
    done = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"Todo({self.id}, {self.todo})"


class TodoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Todo
        include_relationships = True
        load_instance = True


def create(todo, author, category, done):
    """
    Add a to do to the table.
    """
    todo = Todo(todo=todo, author=author, category=category, done=done)
    db.session.add(todo)
    db.session.commit()
    return {"success": True}


def read():
    todos = db.session.query(Todo).all()
    todo_schema = TodoSchema()
    return [todo_schema.dump(t) for t in todos]


def toggle_complete(id):
    """
    """
    todo = db.session.query(Todo).filter(Todo.id == id).first()
    todo.done = not todo.done
    db.session.add(todo)
    db.session.commit()
    return {"success": True}


def delete(id):
    """
    Delete a To Do from the table.
    """
    todo = db.session.query(Todo).filter(Todo.id == id).first()
    db.session.delete(todo)
    db.session.commit()
    return {"success": True}
