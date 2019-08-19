import json

from flask import Blueprint, abort, make_response

from flask_restful import (Resource, Api, reqparse, fields,
                           marshal, marshal_with, url_for)

import models


todos_field = {
    'id': fields.Integer,
    'name': fields.String,
}


def todo_or_404(todo_id):
    try:
        todo = models.Todo.get(models.Todo.id == todo_id)
    except models.Todo.DoesNotExist:
        abort(404)
    else:
        return todo


class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No todo name provided.',
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        todos = [marshal(todo, todos_field) for todo in models.Todo.select()]
        return todos

    @marshal_with(todos_field)
    def post(self):
        args = self.reqparse.parse_args()
        todo = models.Todo.create(**args)
        return todo, 201, {'location': url_for('resources.todos.todo', id=todo.id)}


class Todo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No todo name provided.',
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(todos_field)
    def get(self, id):
        return todo_or_404(id)

    @marshal_with(todos_field)
    def put(self, id):
        args = self.reqparse.parse_args()
        try:
            todo = models.Todo.get(models.Todo.id == id)
        except models.Todo.DoesNotExist:
            abort(404)
        else:
            query = todo.update(**args).where(models.Todo.id == id)
            query.execute()
            return (models.Todo.get(models.Todo.id == id), 200,
                    {'location': url_for('resources.todos.todo', id=id)})

    def delete(self, id):
        try:
            todo = models.Todo.select().where(
                models.Todo.id == id
            ).get()
        except models.Todo.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'That todo does not exist.'}
            ), 403)
        todo.delete_instance()
        return '', 204, {'location': url_for('resources.todos.todos')}


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(
    TodoList,
    '/api/v1/todos',
    endpoint='todos'
)
api.add_resource(
    Todo,
    '/api/v1/todos/<int:id>',
    endpoint='todo'
)
